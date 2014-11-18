# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
=======================================================================
script for batch filename ext change (:mod:`pksci.scripts.mkbkupcp`)
=======================================================================

.. currentmodule:: pksci.scripts.mkbkupcp

.. todo::

   Add option to copy backup file to secondary dst.

.. todo::

   handle exceptions

.. argparse::
   :module: pksci.scripts.mkbkupcp
   :func: argparser
   :prog: mkbkupcp

"""
from __future__ import absolute_import, print_function, division

import argparse
import os
import shutil
import sys
from datetime import datetime

from ..tools import get_fpath


def printmsg(src, dst, srctype):
    print('copied source {!s}: {!s}\n'.format(srctype, src) +
          'to backup {!s}: {!s}'.format(srctype, dst))


def argparser():
    parser = argparse.ArgumentParser()

    default_backup_ext = \
        '.backup_' + datetime.now().strftime("%Y-%m-%d_%H%M%S")

    parser.add_argument('-n', '--numbered', action='store_true',
                        help='create backup copies using numbered file '
                        'extension (default: %(default)s)')
    parser.add_argument('-t', '--timestamped', action='store_true',
                        help='create backup copies using timestamped file '
                        'extension (default: %(default)s)')
    parser.add_argument('-dt', '--datetime', action='store_true',
                        help='create backup copies using date and time file '
                        'extension (default: %(default)s)')
    parser.add_argument('-d', '--datestamped', action='store_true',
                        help='create backup copies using datestamped file '
                        'extension (default: %(default)s)')

    parser.add_argument('-x', '--backup-ext', default=default_backup_ext,
                        help='backup extension (default: %(default)s)')
    parser.add_argument('srclist', nargs='+', help='1 or more files or '
                        'directories to backup')
    return parser


def main():

    args = argparser().parse_args()
    #backup_ext = ''

    #if args.n:
    #    backup_ext += '.bak'

    backup_ext = args.backup_ext

    srclist = args.srclist
    if sys.platform == 'win32':
        from glob import glob
        srclist = glob(srclist[0])

    for src in srclist:
        bkupstr = backup_ext
        dst = src + bkupstr

        if os.path.isfile(src):
            shutil.copy2(src, dst)
            printmsg(src, dst, 'file')
        elif os.path.isdir(src):
            shutil.copytree(src, dst)
            printmsg(src, dst, 'directory')

if __name__ == '__main__':
    sys.exit(main())
