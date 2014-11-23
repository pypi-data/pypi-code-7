# Copyright (C) 2014 Kieran Colford
#
# This file is part of txt2boil.
#
# txt2boil is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# txt2boil is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with txt2boil.  If not, see <http://www.gnu.org/licenses/>.

"""Update the boilerplate in source code.

We do so according to a series of marker comments found through
regexs.

If --in-place is specified then the files are updated in place, if not
then they are printed to stdout.

"""

import argparse
import collections
import sys
import textwrap
import os
from . import langs
from . import language
from . import __version__ as version


def main(argv=sys.argv[1:]):
    """The main method."""

    global ext_lang

    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog)
    parser.add_argument('files', metavar='FILES', nargs='*',
                        help='the files to process')
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument('-i', '--in-place', action='store_true',
                        help='modify files inplace')
    parser.add_argument('--print-langs', action='store_true',
                        help='print out all the supported languages')
    parser.add_argument('--lang', action='store', default='auto',
                        help='use the language with given extention')
    args = parser.parse_args(argv)

    # Print the current set of working languages.
    if args.print_langs:
        parser.print_usage()
        sys.stdout.write('\n')
        sys.stdout.write(textwrap.fill(textwrap.dedent("""\
        The following languages are supported:
        """)) + '\n')
        for cls in sorted({getattr(langs, nm) for nm in langs.__all__}):
            l = cls.__name__
            out = cls.__doc__.split('\n\n')[0]
            out = out + ' (' + ', '.join(cls.ext) + ')'

            prefix2 = ' '.join([''] * 20)
            prefix1 = prefix2[:2] + l + prefix2[2 + len(l):]

            wrapped = textwrap.fill(out, initial_indent=prefix1,
                                    subsequent_indent=prefix2)

            sys.stdout.write(wrapped + '\n')

        parser.exit(0)          # Exit once we're done

    if not args.files:
        parser.print_usage()

    for fname in args.files:
        # load the file
        with open(fname) as f:
            text = f.read()

        # generate the new output according to the language
        if args.lang == 'auto':
            l = language(fname)
        else:
            l = language(args.lang, True)
        text = l.gen(text)

        # emit the output
        if args.in_place:
            with open(fname, 'w') as f:
                f.write(text)
        else:
            sys.stdout.write(text)


description = __doc__
epilog = ''

if __name__ == '__main__':
    main()
