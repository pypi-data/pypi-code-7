# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
=========================================================================
script for batch filename ext change (:mod:`pksci.scripts.change_ext`)
=========================================================================

.. currentmodule:: pksci.scripts.change_ext

.. autofunction:: change_ext

"""
from __future__ import absolute_import, print_function, division

import argparse
import os
import sys
import shutil

__all__ = ['change_ext']


def _argparser():
    ## Set up command line options for OptionParser
    parser = argparse.ArgumentParser()
    parser.add_argument('--ext', required=True,
                        help='new file extension')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    parser.add_argument('files', nargs='+', help='file list')

    return parser


def change_ext(files, ext=None, overwrite=False):
    """Change extension of files.

    Parameters
    ----------
    files : sequence
    ext : str
    overwrite : bool, optional

    """
    if ext is None:
        raise SyntaxError("You need to provide a new file extension")
    if sys.platform == 'win32':
        from glob import glob
        files = glob(files[0])

    # Go through each file
    for f in files:
        if os.path.isfile(f):
            fout = ''
            if ext.startswith('.'):
                fout = os.path.splitext(f)[0] + ext
            else:
                fout = os.path.splitext(f)[0] + '.' + ext
            if os.path.isfile(fout) and not overwrite:
                print('Skipping {!s} file conversion '.format(f) +
                      'because {!s} already exists'.format(fout))
                continue
            else:
                print('Moving {!s} to {!s} '.format(f, fout) +
                      'with new extension {!s}\n'.format(ext))
                shutil.move(f, fout)


def main():

    args = _argparser().parse_args()
    change_ext(**vars(args))

if __name__ == '__main__':
    sys.exit(main())
