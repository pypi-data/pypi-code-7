#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""parsedoc

Parses PHP files to extract docblock comments to Markdown files

Usage:
  parsedoc [options] (<file> | (<directory> <outputdir>))
  parsedoc -h | --help
  parsedoc --version

Options:
  File parse mode:
    <file>                     File to parse
    -o FILE --output=FILE      Output to this file (default: <file>.md)
    --no-output                Don't write output, useful for doc linting

  Directory parse mode:
    <directory>                Directory to parse
    <outputdir>                Directory to put output files
    --pattern=PATTERN          Pattern of filenames to parse [default: *.php]
    --ignore-patterns=PATTERN  Ignore these directories [default: .*]
                               (comma-separated)
    --no-create-index          Don't write index files
    --skip-empty-files         Don't write files which would have no comments

  Filter options:
    --only-include-annotated   Only include specifically annotated functions
                               Implies --skip-empty-files
    --annotations=ANNOTATION   Annotations to include (comma-separated)
                               [default: @API,@APILow]

  General:
    --loglevel=LEVEL           Set log level [default: INFO]
    -h --help                  Show this screen.
    --version                  Show version.
"""
from __future__ import unicode_literals, print_function, with_statement

import logging
import os.path
import sys
from fnmatch import fnmatch

from docopt import docopt
from parsedoc.parser import parse_file
from parsedoc.utils import create_index
from parsedoc.plugins import preprocessing_plugins, postprocessing_plugins

logger = logging.getLogger(__name__)

__version__ = "0.2.0"
__author__ = "Thom Wiggers"
__license__ = "GPLv3"


def main():
    """Main entry point for the parsedoc CLI."""

    args = docopt(__doc__, version=__version__)

    numeric_level = getattr(logging, args['--loglevel'].upper(), None)
    if not isinstance(numeric_level, int):
        print("{} isn't a valid log level.".format(args['--loglevel'].upper()))
        sys.exit(1)
    logging.basicConfig(level=numeric_level)

    # We're in file mode
    if args.get('<file>'):
        if args['<file>'] == '-':
            handle_file('stdin', args.get('--output'), args)
        elif os.path.isfile(args['<file>']):
            handle_file(args['<file>'], args.get('--output'), args)
        elif os.path.isdir(args['<file>']):
            logging.error("%s is a directory. Specify the output directory to "
                          "parse directories.", args['<file>'])
            sys.exit(1)
        else:
            logging.error("Can't open file %s", args['<file>'])
            sys.exit(1)
    # Directory mode
    elif args.get('<directory>') and args.get('<outputdir>'):
        if os.path.isdir(args['<directory>']):
            handle_dir(args['<directory>'],
                       args['<outputdir>'],
                       args.get('--pattern'),
                       args.get('--ignore-patterns').split(','),
                       not args['--no-create-index'],
                       args)
        else:
            logging.error("%s isn't a directory", args['<directory>'])
            sys.exit(1)
    else:  # actually is never executed, but let's be sure
        print("Can't open file or directory {}".format(args['<directory>']))
        sys.exit(1)


def handle_file(filename, output, args):
    """Handles one file and returns if there was any content"""
    if not output:
        output = filename + '.md'
    logger.info("Parsing %s into %s", filename, output)

    if filename == 'stdin':
        file_contents = sys.stdin.read()
        parsed = parse_file('stdinput', file_contents)
    else:
        with open(filename, 'r') as f:
            file_contents = f.read()
            parsed = parse_file(os.path.basename(filename), file_contents)

    # List comprehensions hell yeah
    l = [func(parsed, args) for func in preprocessing_plugins]
    # shut up pylint
    del l

    if (parsed.comment == "" and len(parsed.contains) == 0
            and args['--skip-empty-files']):
        # Would result in empty file, so let's not do this
        logging.info("File %s is skipped because it contained no comments "
                     "to write", filename)
        return False

    if args['--no-output']:
        logging.info("Skipping output")
        return True

    with open(output, 'w') as outfile:
        output = str(parsed)
        outfile.write(output)
        # we apparently wrote something.
        return True


def handle_dir(source_dir_name,
               output_dir,
               pattern,
               exclude_patterns,
               create_indexes,
               args):
    """Parse directories"""

    for (dirpath, dirnames, filenames) in os.walk(source_dir_name):
        dirnames = _filter_dirnames(dirnames, exclude_patterns)
        created_dir = False
        relative_dir_path = os.path.relpath(dirpath, start=source_dir_name)
        current_dir_path = os.path.normpath(
            os.path.join(output_dir, relative_dir_path))

        # do we need to create the directory?
        if not os.path.isdir(current_dir_path):
            logging.debug("Creating dir {}".format(current_dir_path))
            created_dir = True
            os.makedirs(current_dir_path)

        # document the files
        any_content = False
        for filename in filenames:
            if not fnmatch(filename, pattern):
                continue

            # If any file provides results, any_content will be True
            any_content |= handle_file(
                os.path.join(dirpath, filename),
                os.path.join(output_dir,
                             relative_dir_path,
                             "{}.md".format(filename)),
                args)

        if create_indexes and any_content:
            # only create index if we have added anything
            create_index(output_dir, relative_dir_path, dirnames, filenames)
        elif not any_content and created_dir:
            # remove directory if we haven't added anything
            try:
                os.removedirs(current_dir_path)
            except OSError:
                logger.debug("Couldn't remove %s", current_dir_path,
                             exc_info=True)
                pass

    # Postprocessing
    l = [f(args) for f in postprocessing_plugins]
    del l


def _filter_dirnames(dirnames, exclude_patterns):
    """Remove dirnames that match exclude_patterns"""
    for dirname in list(dirnames):
        for exclude_pattern in exclude_patterns:
            if fnmatch(dirname, exclude_pattern):
                dirnames.remove(dirname)
                break
    return dirnames


if __name__ == '__main__':
    main()
