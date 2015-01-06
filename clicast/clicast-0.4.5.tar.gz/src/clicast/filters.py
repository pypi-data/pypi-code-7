import os
import re
import sys


REGEX_IN_MSG_RE = re.compile('^\[(.+)\] *(.+)$', flags=re.DOTALL)
IS_WORD_RE = re.compile('^\w+$')


def match_program_or_subcommand(msg, alert=False, cli_args=None):
  """
  Look for messages that starts with "[program|sub-command] message" and search the program or sub-command against
  the the first two words in the given args (or in sys.argv).

  :param str msg: Message to search
  :param bool alert: Is alert message?
  :param list/str cli_args: Optional args used for testing instead of sys.argv
  :ret str: New message without [program|sub-command] or None if program or sub-command doesn't match CLI args
  """
  match = REGEX_IN_MSG_RE.match(msg)

  if match:
    regex = match.group(1)
    msg = match.group(2)

    if not (regex.startswith('^') or regex.endswith('$')):
      regex = '^(?:%s)$' % regex

    if isinstance(cli_args, str):
      cli_args = cli_args.split()
    elif not cli_args:
      cli_args = sys.argv

    commands = [os.path.basename(cli_args[0])]
    if len(cli_args) > 1 and IS_WORD_RE.match(cli_args[1]):
      commands.append(cli_args[1])

    match = any(re.search(regex, command) for command in commands)
    if not match:
      return None

  return msg


def match_cli_args(msg, alert=False, cli_args=None):
  """
  Look for messages that starts with "[pattern] message" and search the pattern against
  the given args (or sys.argv).

  :param str msg: Message to search
  :param bool alert: Is alert message?
  :param list cli_args: Optional args used for testing instead of sys.argv
  :ret str: New message without [pattern] or None if pattern doesn't match CLI args
  """
  match = REGEX_IN_MSG_RE.match(msg)

  if match:
    regex = match.group(1)
    msg = match.group(2)
    if isinstance(cli_args, str):
      cli_args = cli_args.split()
    args = ' '.join(cli_args or sys.argv)
    if not re.search(regex, args):
      return None

  return msg
