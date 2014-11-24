# =============================================================================
# Copyright [2014] [Kevin Carter]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================
import errno
import hashlib
import os
import subprocess

import cloudlib
from cloudlib import logger


class ShellCommands(object):

    def __init__(self, log_name=__name__, debug=False):
        """Run a shell command on a local Linux Operating System.

        :param log_name: ``str`` This is used to log against an existing log
                                 handler.
        :param debug: ``bol``
        """
        self.log = logger.getLogger(log_name)
        self.debug = debug

    def run_command(self, command, shell=True, env=None, execute='/bin/bash',
                    return_code=None):
        """Run a shell command.

        The options available:

            * ``shell`` to be enabled or disabled, which provides the ability
              to execute arbitrary stings or not. if disabled commands must be
              in the format of a ``list``

            * ``env`` is an environment override and or manipulation setting
              which sets environment variables within the locally executed
              shell.

            * ``execute`` changes the interpreter which is executing the
              command(s).

            * ``return_code`` defines the return code that the command must
              have in order to ensure success. This can be a list of return
              codes if multiple return codes are acceptable.

        :param command: ``str``
        :param shell: ``bol``
        :param env: ``dict``
        :param execute: ``str``
        :param return_code: ``int``
        """
        self.log.info('Command: [ %s ]', command)

        if env is None:
            env = os.environ

        if self.debug is False:
            stdout = open(os.devnull, 'wb')
        else:
            stdout = subprocess.PIPE

        if return_code is None:
            return_code = [0]

        stderr = subprocess.PIPE
        process = subprocess.Popen(
            command,
            stdout=stdout,
            stderr=stderr,
            executable=execute,
            env=env,
            shell=shell
        )

        output, error = process.communicate()

        if process.returncode not in return_code:
            self.log.debug('Command Output: %s, Error Msg: %s', output, error)
            return error, False
        else:
            self.log.debug('Command Output: %s', output)
            return output, True

    def mkdir_p(self, path):
        """Python implementation of `mkdir -p <path>`

        :param path: ``str``
        """
        try:
            if not os.path.isdir(path):
                os.makedirs(path)
                self.log.info('Created Directory [ %s ]', path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise OSError(
                    'The provided path can not be created into a directory.'
                )

    def write_file(self, filename, content):
        """Write a file.

        This is useful when writing a file that will fit within memory

        :param filename: ``str``
        :param content: ``str``
        """
        with open(filename, 'wb') as f:
            self.log.debug(content)
            f.write(content)

    def write_file_lines(self, filename, contents):
        """Write a file.

        This is useful when writing a file that may not fit within memory.

        :param filename: ``str``
        :param contents: ``list``
        """
        with open(filename, 'wb') as f:
            self.log.debug(contents)
            f.writelines(contents)

    @staticmethod
    def read_file(filename):
        """Return the contents of a file.

        :param filename: ``str``
        :return: ``list``
        """
        with open(filename, 'rb') as f:
            return f.read()

    @staticmethod
    def read_file_lines(filename):
        """Return the contents of a file.

        :param filename: ``str``
        :return: ``list``
        """
        with open(filename, 'rb') as f:
            return f.readlines()

    @staticmethod
    def read_large_file_lines(filename):
        """Yield a lines from a file.

        :param filename: ``str``
        :yield: ``object``
        """
        with open(filename, 'rb') as f:
            for line in f.readline():
                yield line

    def md5_checker(self, md5sum, local_file=None, file_object=None):
        """Return True if the local file and the provided `md5sum` are equal.

        If the processed file and the provided md5sum do not match an exception
        is raised indicating the failure.

        :param md5sum: ``str``
        :param local_file: ``str``
        :param file_object: ``BytesIO``
        :return: ``bol``
        """
        def calc_hash():
            """Read the hash.

            :return data_hash.read():
            """
            return file_object.read(128 * md5.block_size)

        if (local_file and os.path.isfile(local_file)) is True or file_object:
            md5 = hashlib.md5()

            if not file_object:
                file_object = open(local_file, 'rb')

            for chk in iter(calc_hash, ''):
                md5.update(chk)
            else:
                if not file_object:
                    file_object.close()

            lmd5sum = md5.hexdigest()
            if md5sum != lmd5sum:
                msg = (
                    'CheckSumm Mis-Match "%s" != "%s" for [ %s ]'
                    % (md5sum, lmd5sum, local_file)
                )
                self.log.error(msg)
                raise cloudlib.MD5CheckMismatch(msg)
            else:
                self.log.info('md5sum verified for [ %s ]', local_file)
                return True

