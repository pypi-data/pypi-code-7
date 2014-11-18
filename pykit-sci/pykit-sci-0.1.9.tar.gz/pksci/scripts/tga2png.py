# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
=====================================================
Command line script (:mod:`pksci.scripts.tga2png`)
=====================================================

Convert TARGA graphic files to PNG format.

.. currentmodule:: pksci.scripts.tga2png

.. argparse::
   :module: pksci.scripts.tga2png
   :func: _argparser
   :prog: tga2png

"""
from __future__ import absolute_import, print_function, division

import argparse
import os
import subprocess
import sys
from os.path import basename, expandvars, join


def file_exists(fpath, dirlist):
    """Check if file exists in fpath or in dirlist.

    Parameters
    ----------
    fpath : str
        absolute path of file
    dirlist : list
        list of absolute directory paths to check

    Returns
    -------
    fexistence : bool
        True if file exists in working directory or in dirlist outpath,
        otherwise False

    """
    fexistence = False
    if os.path.isfile(fpath):
        fexistence = True
    else:
        cwdtree = getcwdtree(os.getcwd())
        for d in dirlist:
            outpath = makedirs(d, cwdtree)
            if outpath is not None:
                new_fpath = join(outpath, fpath)
                if os.path.isfile(new_fpath):
                    fexistence = True
                    break

    return fexistence


def getcwdtree(path):
    """Get directory tree list below the 'figures' directory pathname.

    Parameters
    ----------
    path : str
        pathname

    Results
    -------
    cwdtree : str
        pathname of cwdtree

    """
    cwdtree = []
    startdir = os.getcwd()
    curdir = basename(startdir)
    homedir = expandvars('$HOME')
    #dropbox_figures = join(homedir, 'Dropbox', 'figures')
    #skydrive_figures = join(homedir, 'SkyDrive', 'NPRL', 'figures')
    while (curdir != 'figures') and (curdir != basename(homedir)):
        cwdtree.insert(0, curdir)
        os.chdir(os.pardir)
        curdir = basename(os.getcwd())
    #if os.getcwd() == dropbox_figures:
    os.chdir(startdir)
    return cwdtree


def makedirs(parentpath, dirtree):
    """Recursively make dirs in dirtree list within the parentdir dirname.

    Parameters
    ----------
    parentpath : str
        absolute pathname in which to make directory tree
    dirtree : list
        list of directories to iterate through and recursively make

    Returns
    -------
    fullpath : str or None
        absolute path if directory tree was generated successfully,
        otherwise return None

    """
    fullpath = parentpath
    for d in dirtree:
        fullpath = join(fullpath, d)
    if not os.path.isdir(fullpath):
        try:
            os.makedirs(fullpath)
        except OSError as e:
            fullpath = None
            print(e)

    return fullpath


def _argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    parser.add_argument('tgafiles', nargs='+', help='tga files')
    return parser


def tga2png(files, overwrite=False):

    #dirlist = []
    #homedir = expandvars('$HOME')
    #dropbox_figures = join(homedir, 'Dropbox', 'figures')
    #dirlist.append(dropbox_figures)
    #skydrive_figures = join(homedir, 'SkyDrive', 'NPRL', 'figures')
    #dirlist.append(skydrive_figures)

    for f in files:
        if os.path.isfile(f) and f.lower().endswith('.tga'):
            fout = os.path.splitext(f)[0] + '.png'
            if os.path.isfile(fout) and not overwrite:
            #if file_exists(fout, dirlist) and not overwrite:
                print('{!s} already exists.\n'.format(fout) +
                      'Use ``--overwrite`` to overwrite existing file\n' +
                      'Moving on...')
                continue
            else:
                print('Converting {!s}'.format(f))
                retcode = subprocess.call(["convert", f, fout])
                if retcode != 0:
                    print('failed to convert {!s}. Moving on...'.format(f))
                    continue
                else:
                    print('successfully converted ' +
                          '{!s} to {!s}'.format(f, fout))
    print("Done!")


def main():

    args = _argparser().parse_args()

    files = args.tgafiles
    if sys.platform == 'win32':
        from glob import glob
        files = glob(files[0])

    tga2png(files, overwrite=args.overwrite)

if __name__ == '__main__':
    sys.exit(main())
