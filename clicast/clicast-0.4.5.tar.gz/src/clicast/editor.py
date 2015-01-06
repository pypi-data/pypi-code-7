"""
An utility script to help create or edit cast files.

Example Action                | Run Command
==============================================================
View current cast             | cast
--------------------------------------------------------------
Add a new message to new file | cast "New Message" -f new.cast
To delete a message           | cast -d
--------------------------------------------------------------
Set an alert message          | cast "New Alert" -a
Unset an alert                | cast -d -a
--------------------------------------------------------------
"""

import argparse
from glob import glob
import logging
import os
import sys

from clicast.cast import Cast


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger(__name__)


def cast():
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-a', '--alert', action='store_true', help='Indicates this is an alert message')
  parser.add_argument('-e', '--alert-exit', action='store_true', help='Indicates this is an alert message with exit = True')
  parser.add_argument('-f', '--file', help='New or existing cast file to update. Defaults to any cast file in current directory.')
  group = parser.add_mutually_exclusive_group()
  group.add_argument('msg', nargs='?', help='The message to cast')
  group.add_argument('--delete', type=int, metavar='COUNT', nargs='?', const=1,
                     help='Delete the oldest message (default) or the number of messages (oldest first). '
                          'Use with --alert to remove the alert message')
  group.add_argument('--limit', type=int, metavar='COUNT',
                     help='Set limit on total number of messages by deleting oldest message as new message is added '
                          'when limit has been reached.')

  args = parser.parse_args()

  cast, cast_file = cast_info_from_path(args.file)

  if args.delete:
    cast.del_msg(args.delete, args.alert or args.alert_exit)

  elif args.limit:
    cast.set_msg_limit(args.limit)

  elif args.msg:
    cast.add_msg(args.msg, args.alert, args.alert_exit)

  elif not os.path.exists(cast_file):
    log.error('%s does not exist', cast_file)
    sys.exit(1)

  cast.save(cast_file)

  print str(cast).strip()


def cast_info_from_path(cast_file=None):
  if cast_file:
    if os.path.exists(cast_file):
      cast = Cast.from_content(cast_file)
    else:
      cast = Cast()

  else:
    cast_files = glob('*.cast')

    if not cast_files:
      log.error('There is no cast file. To create a new one, specify the name with --file')
      sys.exit(1)

    if len(cast_files) > 1:
      log.error('There are more than one cast file. Please specify which to modify with --file')
      sys.exit(1)

    cast_file = cast_files[0]
    cast = Cast.from_content(cast_file)

  return cast, cast_file
