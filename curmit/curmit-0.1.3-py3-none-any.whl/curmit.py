#!/usr/bin/env python

"""Grabs text from a URL and commits it."""

import os
import re
import sys
import subprocess
import argparse
import logging

from curmit import CLI, VERSION

# User settings
IGNORED_DIRNAMES = ('.git', 'env', '.cache')
MAX_SEARCH_LINE = 5

# Constants
RE_FLAG = re.compile(r"""
\bcurmit:       # the flag
\               # a space
(?P<url>\S+)    # any non-whitespace (the URL)
""", re.VERBOSE)

# Logging settings
DEFAULT_LOGGING_FORMAT = "%(message)s"
VERBOSE_LOGGING_FORMAT = "%(levelname)s: %(message)s"
VERBOSE2_LOGGING_FORMAT = "[%(levelname)-8s] %(message)s"
DEFAULT_LOGGING_LEVEL = logging.WARNING
VERBOSE_LOGGING_LEVEL = logging.INFO
VERBOSE2_LOGGING_LEVEL = logging.DEBUG


class HelpFormatter(argparse.HelpFormatter):  # pylint: disable=R0903

    """Command-line help text formatter with wider help text."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, max_help_position=40, **kwargs)


class WarningFormatter(logging.Formatter, object):  # pylint: disable=R0903

    """Logging formatter with verbose logging for WARNING and higher."""

    def __init__(self, default_format, verbose_format, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_format = default_format
        self.verbose_format = verbose_format

    def format(self, record):  # pragma: no cover, manual test
        """Python 3 hack to change the formatting style dynamically."""
        if record.levelno > logging.INFO:
            self._style._fmt = self.verbose_format  # pylint: disable=W0212
        else:
            self._style._fmt = self.default_format  # pylint: disable=W0212
        return super().format(record)

# Shared command-line arguments
DEBUG = argparse.ArgumentParser(add_help=False)
DEBUG.add_argument('-V', '--version', action='version', version=VERSION)
DEBUG.add_argument('-v', '--verbose', action='count', default=0,
                   help="enable verbose logging")
SHARED = {'formatter_class': HelpFormatter, 'parents': [DEBUG]}


def main(args=None):
    """Process command-line arguments and run the program."""
    # Main parser
    parser = argparse.ArgumentParser(prog=CLI, description=__doc__, **SHARED)
    parser.add_argument('--no-update', action='store_true',
                        help="do not modify files, just display contents")
    parser.add_argument('--no-commit', action='store_true',
                        help="do not commit changes to files")

    # Parse arguments
    args = parser.parse_args(args=args)

    # Configure logging
    _configure_logging(args.verbose)

    # Run the program
    try:
        success = _run(args, os.getcwd(), parser.error)
    except KeyboardInterrupt:
        logging.debug("command cancelled")
        success = False
    if success:
        logging.debug("command succeeded")
    else:
        logging.debug("command failed")
        sys.exit(1)


def _configure_logging(verbosity=0):
    """Configure logging using the provided verbosity level (0+)."""
    # Configure the logging level and format
    if verbosity == 0:
        level = DEFAULT_LOGGING_LEVEL
        default_format = DEFAULT_LOGGING_FORMAT
        verbose_format = VERBOSE_LOGGING_FORMAT
    elif verbosity == 1:
        level = VERBOSE_LOGGING_LEVEL
        default_format = DEFAULT_LOGGING_FORMAT
        verbose_format = VERBOSE_LOGGING_FORMAT
    else:
        level = VERBOSE2_LOGGING_LEVEL
        default_format = verbose_format = VERBOSE2_LOGGING_FORMAT

    # Set a custom formatter
    logging.basicConfig(level=level)
    formatter = WarningFormatter(default_format, verbose_format)
    logging.root.handlers[0].setFormatter(formatter)


def _run(args, cwd, err):  # pylint: disable=W0613
    """Process arguments and run the main program.

    @param args: Namespace of CLI arguments
    @param cwd: current working directory
    @param err: function to call for CLI errors
    """
    git('reset', _dry=args.no_commit)
    changes = False

    for path, header, url in flagged(cwd):
        lines = header + urltext(url)
        logging.info("updating {}...".format(path))
        if args.no_update:
            for line in lines:
                print(line)
        else:
            with open(path, 'w') as outfile:
                for line in lines:
                    outfile.write(line + '\n')

        git('add', path, _dry=args.no_commit)
        if git('diff', '--cached', '--exit-code'):
            logging.info("committing {}...".format(path))
            message = "curmit: {}".format(url.replace("/pub?embedded=true",
                                                      '/edit'))
            git('commit', '-m', message, _show=True, _dry=args.no_commit)
            changes = True
        else:
            logging.info("no change: {}".format(path))

    if changes:
        logging.info("pushing changes...")
        git('push', _show=True, _dry=args.no_commit)

    return True


def flagged(cwd):  # pylint: disable=R0912
    """Yield every text file containing a flag.

    @return: generator of path, flag text, URL
    """
    logging.info("looking for flagged files...")
    for root, dirnames, filenames in os.walk(cwd):

        # Remove ignored directory names
        for ignored_dirname in IGNORED_DIRNAMES:
            if ignored_dirname in dirnames:
                dirnames.remove(ignored_dirname)

        # Locate all flagged files
        for filename in filenames:
            path = os.path.join(root, filename)
            try:
                with open(path, 'r') as infile:
                    url = None
                    header = []
                    for index, line in enumerate(infile, start=1):

                        header.append(line)

                        if url:
                            if not line.strip():
                                break  # blank line after found flag
                        else:
                            match = RE_FLAG.search(line)
                            if match:
                                url = match.group('url')

                        if index >= MAX_SEARCH_LINE:
                            break
                    if url:
                        logging.info("found flag in: {}".format(path))
                        yield path, header, url
                    else:
                        logging.info("no flag in: {}".format(path))

            except UnicodeDecodeError:
                logging.debug("skipped: {}".format(path))


def urltext(url):
    """Get lines of text from a URL."""
    logging.info("grabbing {}...".format(url))

    # Build commands
    args2 = [sys.executable, '-m', 'html2text']
    args2.append(url)
    args1 = args2.copy()
    if 'docs.google.com' in url:
        args1.append('--google-doc')

    # Try commands
    for args in (args1, args2):
        logging.debug("$ {}".format(' '.join(str(a) for a in args)))
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        out = process.communicate()[0]
        text = out.decode('utf-8')  # pylint: disable=E1101
        lines = text.strip().split('\n')
        if process.returncode == 0:
            break
        elif args != args2:
            logging.warning("trying again with different arguments...")

    # Check for errors
    if process.returncode != 0:
        raise IOError("error running 'html2text'")

    return lines


def git(*args, _show=False, _dry=False):
    """Call git with arguments."""
    if _dry:
        args = ['git #'] + list(args)
    else:
        args = ['git'] + list(args)
    logging.debug("$ {}".format(' '.join(str(a) for a in args)))
    if _dry:
        return 0
    if _show:
        return subprocess.call(args)
    else:
        devnull = open(os.devnull, 'w')
        return subprocess.call(args, stdout=devnull, stderr=subprocess.STDOUT)


if __name__ == '__main__':  # pragma: no cover, manual test
    main()
