#!/usr/bin/env python
"""
Simple command line pyscript to batch convert one or more gifs to jpgs.

author: Andrew Merrill

Revision: $Id$

"""

#TODO: Test on a Windows box
#TODO: Upgrade string encoding to unicode
#TODO: improve docstrings

import argparse
import os
import subprocess
import sys

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite', action='store_true',
            help='overwrite existing files')
    parser.add_argument('gifs', nargs='+', help='gif files')
    args = parser.parse_args()
    overwrite = args.overwrite
    files = args.gifs
    for f in files:
        if os.path.isfile(f) and f.lower().endswith('.gif'):
            fout = os.path.splitext(f)[0] + '.eps'
            if os.path.isfile(fout) and not overwrite:
                print('Skipping {!s} file conversion '.format(f) + \
                        'because {!s} already exists'.format(fout))
                continue
            else:
                print('Converting {!s} to {!s}\n'.format(f, fout))
                retcode = subprocess.call(["convert", f, fout])
                if retcode != 0:
                    print('command failure\n')
                else:
                    print('command success!\n')

if __name__ == '__main__':
    sys.exit(main())
