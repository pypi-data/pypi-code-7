#!/usr/bin/env python
"""
Convert EPS files to png files.

"""

import argparse
import os
import subprocess
import sys

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite', action='store_true',
            help='overwrite existing files')
    parser.add_argument('epsfiles', nargs='+', help='eps files')
    args = parser.parse_args()
    overwrite = args.overwrite
    files = args.epsfiles
    for f in files:
        if os.path.isfile(f) and f.lower().endswith('.eps'):
            fout = os.path.splitext(f)[0] + '.png'
            if os.path.isfile(fout) and not overwrite:
                print('Skipping {!s} file conversion '.format(f) + \
                        'because {!s} already exists'.format(fout))
                continue
            else:
                print('Converting {!s} to {!s}'.format(f, fout))
                retcode = subprocess.call(["convert", f, fout])
                if retcode != 0:
                    print('command failure\n')
                else:
                    print('command success!\n')

if __name__ == '__main__':
    sys.exit(main())
