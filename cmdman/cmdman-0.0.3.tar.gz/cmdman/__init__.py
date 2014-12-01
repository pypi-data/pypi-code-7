# Author: Franck Michea <franck.michea@gmail.com>
# License: New BSD License (See LICENSE)

from __future__ import print_function

import argparse
import pdb
import sys
import textwrap
import traceback


class CMDMAN_CMDError(Exception):
    pass


class cmdman:
    def __init__(self, **kwargs):
        # Error header is the text displayed before an error that is a subclass
        # of CMDError.
        self._error_header = kwargs.pop('error_header', 'ERROR: ')
        # Width of the error message. Text will be wrapped to fit in that width.
        self._width = kwargs.pop('error_width', 70)
        # An user might want to avoid having the library exit for him, so we
        # give the choice to configure that. This will catch exits from
        # argparse, and raise return the code instead.
        self._should_exit = kwargs.pop('should_exit', True)
        # The user might want to get a function called instead of help when no
        # 'func' is found (automatically called sub-parser functions.
        self._default_func = kwargs.pop('default_func', self._default_print_help)
        # Create the main parser with the arguments given by the user.
        kwds = kwargs.pop('ap_kwds', dict())
        # The whole parameter grabbing is done, if we have some arguments left,
        # then the user probably did a mistake and we raise TypeError as would
        # a standard function not using **kwargs.
        if kwargs:
            msg = '__init__() got '
            keys = ', '.join("'{}'".format(k) for k in kwargs.keys())
            if 1 < len(kwargs.keys()):
                msg += 'unexpected keyword arguments ' + keys
            else:
                msg += 'an unexpected keyword argument ' + keys
            raise TypeError(msg)
        # We can now use all those values and configure the parser.
        parser = argparse.ArgumentParser(**kwds)
        # We can now add all the default arguments necessary.
        ## Debugging options.
        parser.add_argument('-b', '--backtrace', action='store_true', default=False,
                            help='print backtrace on error (default with --pdb)')
        parser.add_argument('-P', '--pdb', action='store_true', default=False,
                            help='launch pdb on error')
        # Finally set the parser to an attribute of our object.
        self.parser, self._subparsers = parser, None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def add_subparser(self, name, func, **kwargs):
        if self._subparsers is None:
            self._subparsers = self.parser.add_subparsers()
        subparser = self._subparsers.add_parser(name, **kwargs)
        subparser.set_defaults(func=func)
        return subparser

    def parse(self, args=None):
        if args is None:
            args = sys.argv[1:]

        try:
            args = self.parser.parse_args(args)
        except SystemExit as e:
            if self._should_exit:
                raise
            return e.code

        try:
            if hasattr(args, 'func'):
                return args.func(args)
            return self._default_func(args)
        except Exception as e:
            # Since we raise back exceptions that are not instances of
            # CMDMAN_CMDError, we don't want to print the stacktrace ourselves
            # unless we are asked to pdb, in which case the type of exception
            # does not matter.
            if args.pdb or (args.backtrace and isinstance(e, CMDMAN_CMDError)):
                traceback.print_exc()
            if args.pdb:  # Are we going to pdb that?
                pdb.post_mortem(sys.exc_info()[2])
            else:  # Otherwise we re-raise the exception or display it properly.
                if not isinstance(e, CMDMAN_CMDError):
                    raise
                if not args.backtrace:
                    print(self._format_error(e), file=sys.stderr)
            return 1

    def _default_print_help(self, _):
        self.parser.print_help(file=sys.stderr)
        return 1

    def _format_error(self, e):
        output, indent_size = [], len(self._error_header)
        # For each "paragraph", wrap on size minus the size of the indent
        # necessary for the header, then add that indent to all the lines.
        for txt in str(e).splitlines():
            output.append('\n'.join('{indent_char:{indent_size}s}{txt}'.format(
                indent_char = ' ',
                indent_size = indent_size,
                txt = txt
            ) for txt in textwrap.wrap(txt, width=(self._width - indent_size))))
        # Join all the paragraphs and add the header before the first one.
        res = '\n\n'.join(output)
        res = self._error_header + res[len(self._error_header):]
        return res
