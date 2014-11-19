# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
==================================================================
Convert TIFF files to EPS files (:mod:`pksci.scripts.tiff2eps`)
==================================================================

.. currentmodule:: pksci.scripts.tiff2eps

.. autofunction:: tiff2eps

"""

import argparse
import os
import subprocess
import sys

__all__ = ['tiff2eps']


def tiff2eps(files, overwrite=False):
    """Convert TIIF files to EPS files.

    Parameters
    ----------
    files : sequence
    overwrite : bool, optional

    """
    for f in files:
        if f.lower().endswith('.tif') or f.lower().endswith('.tiff') \
                and os.path.isfile(f):
            fout = os.path.splitext(f)[0] + '.eps'
            if os.path.isfile(fout) and not overwrite:
                print('Skipping {!s} file conversion '.format(f) +
                      'because {!s} already exists'.format(fout))
                continue
            else:
                print('Converting {!s} to {!s}\n'.format(f, fout))
                retcode = subprocess.call(["convert", f, fout])
                if retcode != 0:
                    print('command failure\n')
                else:
                    print('command success!\n')


def _argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    parser.add_argument('files', nargs='+', help='tiff files')
    return parser


def main():

    args = _argparser().parse_args()
    tiff2eps(**vars(args))

if __name__ == '__main__':
    sys.exit(main())
