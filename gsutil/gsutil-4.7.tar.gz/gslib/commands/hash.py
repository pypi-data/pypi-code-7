# -*- coding: utf-8 -*-
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Implementation of hash command for calculating hashes of local files."""

from hashlib import md5
import os

import crcmod

from gslib.command import Command
from gslib.command_argument import CommandArgument
from gslib.cs_api_map import ApiSelector
from gslib.exception import CommandException
from gslib.hashing_helper import Base64EncodeHash
from gslib.hashing_helper import CalculateHashesFromContents
from gslib.hashing_helper import SLOW_CRCMOD_WARNING
from gslib.progress_callback import ConstructAnnounceText
from gslib.progress_callback import FileProgressCallbackHandler
from gslib.progress_callback import ProgressCallbackWithBackoff
from gslib.storage_url import StorageUrlFromString
from gslib.util import NO_MAX
from gslib.util import UsingCrcmodExtension

_SYNOPSIS = """
  gsutil [-c] [-h] [-m] hash filename...
"""

_DETAILED_HELP_TEXT = ("""
<B>SYNOPSIS</B>
""" + _SYNOPSIS + """


<B>DESCRIPTION</B>
  The hash command calculates hashes on a local file that can be used to compare
  with gsutil ls -L output. If a specific hash option is not provided, this
  command calculates all gsutil-supported hashes for the file.

  Note that gsutil automatically performs hash validation when uploading or
  downloading files, so this command is only needed if you want to write a
  script that separately checks the hash for some reason.

  If you calculate a CRC32c hash for the file without a precompiled crcmod
  installation, hashing will be very slow. See "gsutil help crcmod" for details.

<B>OPTIONS</B>
  -c          Calculate a CRC32c hash for the file.

  -h          Output hashes in hex format. By default, gsutil uses base64.

  -m          Calculate a MD5 hash for the file.
""")


class HashCommand(Command):
  """Implementation of gsutil hash command."""

  # Command specification. See base class for documentation.
  command_spec = Command.CreateCommandSpec(
      'hash',
      command_name_aliases=[],
      usage_synopsis=_SYNOPSIS,
      min_args=1,
      max_args=NO_MAX,
      supported_sub_args='chm',
      file_url_ok=True,
      provider_url_ok=False,
      urls_start_arg=0,
      gs_api_support=[ApiSelector.JSON],
      gs_default_api=ApiSelector.JSON,
      argparse_arguments=[
          CommandArgument.MakeZeroOrMoreFileURLsArgument()
      ]
  )
  # Help specification. See help_provider.py for documentation.
  help_spec = Command.HelpSpec(
      help_name='hash',
      help_name_aliases=['checksum'],
      help_type='command_help',
      help_one_line_summary='Calculate file hashes',
      help_text=_DETAILED_HELP_TEXT,
      subcommand_help_text={},
  )

  @classmethod
  def _ParseOpts(cls, sub_opts, logger):
    """Returns behavior variables based on input options.

    Args:
      sub_opts: getopt sub-arguments for the command.
      logger: logging.Logger for the command.

    Returns:
      Tuple of
      calc_crc32c: Boolean, if True, command should calculate a CRC32c checksum.
      calc_md5: Boolean, if True, command should calculate an MD5 hash.
      format_func: Function used for formatting the hash in the desired format.
      output_format: String describing the hash output format.
    """
    calc_crc32c = False
    calc_md5 = False
    format_func = lambda digest: Base64EncodeHash(digest.hexdigest())
    found_hash_option = False
    output_format = 'base64'

    if sub_opts:
      for o, unused_a in sub_opts:
        if o == '-c':
          calc_crc32c = True
          found_hash_option = True
        elif o == '-h':
          output_format = 'hex'
          format_func = lambda digest: digest.hexdigest()
        elif o == '-m':
          calc_md5 = True
          found_hash_option = True

    if not found_hash_option:
      calc_crc32c = True
      calc_md5 = True

    if calc_crc32c and not UsingCrcmodExtension(crcmod):
      logger.warn(SLOW_CRCMOD_WARNING)

    return calc_crc32c, calc_md5, format_func, output_format

  def _GetHashClassesFromArgs(self, calc_crc32c, calc_md5):
    """Constructs the dictionary of hashes to compute based on the arguments.

    Args:
      calc_crc32c: If True, CRC32c should be included.
      calc_md5: If True, MD5 should be included.

    Returns:
      Dictionary of {string: hash digester}, where string the name of the
          digester algorithm.
    """
    hash_dict = {}
    if calc_crc32c:
      hash_dict['crc32c'] = crcmod.predefined.Crc('crc-32c')
    if calc_md5:
      hash_dict['md5'] = md5()
    return hash_dict

  def RunCommand(self):
    """Command entry point for the hash command."""
    (calc_crc32c, calc_md5, format_func, output_format) = (
        self._ParseOpts(self.sub_opts, self.logger))

    matched_one = False
    for url_str in self.args:
      if not StorageUrlFromString(url_str).IsFileUrl():
        raise CommandException('"hash" command requires a file URL')

      for file_ref in self.WildcardIterator(url_str).IterObjects():
        matched_one = True
        file_name = file_ref.storage_url.object_name
        file_size = os.path.getsize(file_name)
        callback_processor = ProgressCallbackWithBackoff(
            file_size, FileProgressCallbackHandler(
                ConstructAnnounceText('Hashing', file_name), self.logger).call)
        hash_dict = self._GetHashClassesFromArgs(calc_crc32c, calc_md5)
        with open(file_name, 'rb') as fp:
          CalculateHashesFromContents(fp, hash_dict,
                                      callback_processor=callback_processor)
        print 'Hashes [%s] for %s:' % (output_format, file_name)
        for name, digest in hash_dict.iteritems():
          print '\tHash (%s):\t\t%s' % (name, format_func(digest))

    if not matched_one:
      raise CommandException('No files matched')

    return 0

