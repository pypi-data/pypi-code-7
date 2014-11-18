# -*- coding: utf-8 -*-
"""
========================================================================
Utility functions for file io (:mod:`pksci.tools._fiofuncs`)
========================================================================

.. currentmodule:: pksci.tools._fiofuncs

"""
from __future__ import division, print_function, absolute_import

import os
import re
import sys

__all__ = ['file_exists', 'get_fpath', 'getcwdtree', 'makedirs']


def file_exists(fpath, dirlist, subdir=None):
    """Check if file exists in fpath or in dirlist.

    Parameters
    ----------
    fpath : str
        absolute path of file
    dirlist : list
        list of absolute directory paths to check
    subdir : str, optional
        subdirectory to join to path

    Returns
    -------
    fexistence : bool
        True if file exists in working directory or in dirlist outpath,
        otherwise False

    """

    fexistence = False
    if subdir is not None:
        os.chdir(subdir)

    if os.path.isfile(fpath):
        fexistence = True
    else:
        cwdtree = getcwdtree(os.getcwd())
        for d in dirlist:
            outpath = makedirs(d, cwdtree)
            if outpath is not None:
                new_fpath = os.path.join(outpath, fpath)
                if os.path.isfile(new_fpath):
                    fexistence = True
                    break

    if subdir is not None:
        os.chdir(os.pardir)

    return fexistence


def get_fpath(fname=None, ext=None, outpath=os.getcwd(), overwrite=False,
              add_fnum=True, fnum=None, include_fname=False, fname_only=False,
              verbose=False):
    """Generate modified `fname` string based on chosen parameters.

    Parameters
    ----------
    fname : str
        Name of file, with or without an extension.
    ext : str, optional
        File extension to append to `fname`. If `ext` is None,
        then `fname` is analyzed to see if it likely already has an
        extension. An extension is set to the
        last element in the list of strings returned by
        `fname.split('.')` **if** this list has more than 1 element.
        Otherwise, `ext` will be set to an empty string `''`.
        If `ext` is not None and is a valid string,
        then `fname` is analyzed to see if it already ends with `ext`.
        If `fname.endswith(ext)` is True from the start, then `ext` will
        not be duplicately appended.
    outpath : str, optional
        Absolute or relative path for generated output file.
        Default is the absolute path returned by `os.getcwd()`.
    overwrite : bool, optional
        If True, overwrite an existing file if it has the same generated
        file path.
    add_fnum : bool, optional
        Append integer number to output file name, starting with **1**.

        .. versionchanged:: 0.1.7
           Changed default to True.

    fnum : {None, int}, optional
        Starting file number to append if `add_fnum` is True.

        .. note::

        If the generated file path exists and `overwrite` is False,
        setting this parameter has no effect.

    include_fname : bool, optional
        If True, return `(fpath, fname)` tuple.
    fname_only : bool, optional
        If True, return only `fname`.

        .. versionadded:: 0.1.7

    verbose : bool, optional
        Show verbose output.

    Returns
    -------
    fpath : str
        The concatenation of `outpath` followed by the updated `fname`.
    (fpath, fname) : tuple (only if `include_fname` is True)
        2-tuple of strings `(fpath, fname)`.
    fname : str (only if `fname_only` is True)
        Updated `fname`.

    """
    f = None
    if fname is None or fname == '':
        error_msg = '`fname` must be a string at least 1 character long.'
        if fname is None:
            raise TypeError(error_msg)
        else:
            raise ValueError(error_msg)
    else:
        f = fname
        fsplit = f.split('.')
        if ext is None:
            if len(fsplit) > 1:
                ext = '.' + fsplit[-1]
            else:
                ext = ''
        else:
            # check if extension already starts with a '.'
            if not ext.startswith('.'):
                ext = '.' + ext
            # check if file name already ends with extension.
            if f.split('.')[-1] != ext.split('.')[-1]:
                f += ext

    if add_fnum:
        fname = re.split(ext, f)[0]
        if fnum is not None:
            f = fname + '-{:d}'.format(fnum) + ext
        else:
            f = fname + '-1' + ext

    fpath = None

    try:
        os.makedirs(outpath)
    except OSError:
        if os.path.isdir(outpath):
            pass
        else:
            outpath = os.curdir
    finally:
        fname = f
        fpath = os.path.join(outpath, fname)
        if os.path.isfile(fpath):
            if overwrite:
                try:
                    os.remove(fpath)
                except OSError as e:
                    print(e)
                    sys.exit(1)
                else:
                    if verbose:
                        print(u'overwriting existing file: {}'.format(fname))
            else:
                if add_fnum:
                    while os.path.isfile(fpath):
                        fname = \
                            '-'.join(re.split('-', re.split(ext, f)[0])[:-1])
                        fnum = re.split('-', re.split(ext, f)[0])[-1]
                        f = fname + '-' + str(int(fnum) + 1) + ext
                        fpath = os.path.join(outpath, f)
                    fname = f
                else:
                    print(u'file exists: {}\n'.format(fpath) +
                          u'Set `add_fnum=True` to generate unique `fname`\n'
                          u'or `overwrite=True` to overwrite existing '
                          u'file.')
                    fpath = None

        if verbose:
            print(u'Generated file name: {}'.format(fname))
            print(u'File path: {}'.format(fpath))

        if fname_only:
            return fname
        elif include_fname:
            return fpath, fname
        else:
            return fpath


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
    curdir = os.path.basename(startdir)
    homedir = os.path.expandvars('$HOME')
    #dropbox_figures = join(homedir, 'Dropbox', 'figures')
    #skydrive_figures = join(homedir, 'SkyDrive', 'NPRL', 'figures')
    while (curdir != 'figures') and (curdir != os.path.basename(homedir)):
        cwdtree.insert(0, curdir)
        os.chdir(os.pardir)
        curdir = os.path.basename(os.getcwd())
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
        fullpath = os.path.join(fullpath, d)
    if not os.path.isdir(fullpath):
        try:
            os.makedirs(fullpath)
        except OSError as e:
            fullpath = None
            print(e)

    return fullpath
