#!/usr/bin/env python
"""
Convert TARGA graphic files to JPG format.

"""

import argparse
import os
import subprocess
import sys

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite', action='store_true',
            help='overwrite existing files')
    parser.add_argument('tgafiles', nargs='+', help='tga files')
    args = parser.parse_args()
    overwrite = args.overwrite
    files = args.tgafiles
    for f in files:
        if os.path.isfile(f) and f.lower().endswith('.tga'):
            fout = os.path.splitext(f)[0] + '.jpg'
            if os.path.isfile(fout) and not overwrite:
                print('Skipping {!s} conversion...'.format(f) + \
                        'file {!s} exists'.format(fout))
                continue
            else:
                print('Converting {!s} to {!s}'.format(f, fout))
                retcode = subprocess.call(["convert", f, fout])
                if retcode != 0:
                    print('Failed to convert {!s}'.format(f))
                else:
                    print('Converted {!s} to {!s}'.format(f, fout))
    print "Done!"

if __name__ == '__main__':
    sys.exit(main())
