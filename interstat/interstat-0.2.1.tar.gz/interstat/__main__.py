"""Command line entry points."""


from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import argparse
import io
import os.path

from pkg_resources import require

from . import __name__ as PACKAGE_NAME, file_as_html
from .formats import formats


def main():
    """Default command line entry point."""
    parser = argparse.ArgumentParser(
        description='Format IRC log files as HTML.')
    parser.add_argument(
        '-f', dest='format', metavar='FORMAT',
        choices=formats, default='omnipresence',
        help='log format (default: omnipresence)')
    parser.add_argument(
        '-l', dest='list_formats', action='store_true',
        help='list known formats and exit')
    parser.add_argument(
        '--stylesheet', metavar='URI',
        help='use stylesheet URI instead of inlining default styles')
    parser.add_argument(
        '--template-dir', metavar='DIR',
        help='override the default templates with those in DIR')
    parser.add_argument(
        '--title',
        help='HTML page <title> (default: log file basename)')
    parser.add_argument(
        '--variable', dest='variables', metavar='KEY=VALUE',
        action='append', default=[],
        help='specify a custom template variable '
             '(may be used multiple times)')
    parser.add_argument(
        '--version', action='version',
        version='%(prog)s ' + require(PACKAGE_NAME)[0].version)
    parser.add_argument(
        'log_path', metavar='LOGFILE', nargs='?',
        help='log file to format (default: stdin)')
    parser.add_argument(
        'html_path', metavar='HTMLFILE', nargs='?',
        help='output HTML file (default: stdout)')
    args = parser.parse_args()
    if args.list_formats:
        print(', '.join(formats))
        return
    # Manually using io.open instead of delegating to argparse.FileType
    # is necessary here because the latter yields byte strings instead
    # of Unicode strings on Python 2, causing UnicodeDecodeErrors down
    # the line.  This can be reverted when Python 2 support is dropped.
    log_file = io.open(args.log_path or 0)
    # Handle custom template variables.
    kwargs = dict()
    kwargs['title'] = (args.title or
                       os.path.splitext(os.path.basename(log_file.name))[0])
    if args.stylesheet is not None:
        kwargs['stylesheet'] = args.stylesheet
    for declaration in args.variables:
        key, sep, value = declaration.partition('=')
        if not sep:
            parser.error('invalid variable declaration "{}"'
                         .format(declaration))
        kwargs[key] = value
    html = file_as_html(
        log_file, args.format, template_dir=args.template_dir, **kwargs)
    html_file = io.open(args.html_path or 1, 'w')  # Same as above.
    html_file.write(html)


if __name__ == '__main__':
    main()
