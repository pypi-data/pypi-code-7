#!/usr/bin/env python
"""
Convert PPM graphic files to PNG format.

"""

import argparse
import os
import subprocess
import sys

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite', action='store_true',
            help='overwrite existing files')
    parser.add_argument('ppmfiles', nargs='+', help='ppm files')
    args = parser.parse_args()
    overwrite = args.overwrite
    files = args.ppmfiles
    for f in files:
        if os.path.isfile(f) and f.lower().endswith('.ppm'):
            fout = os.path.splitext(f)[0] + '.png'
            if os.path.isfile(fout) and not overwrite:
                print('{!s} already exists.\n'.format(fout) + \
                        "Use '--overwrite' to overwrite existing file\n" + \
                        'Moving on...')
                continue
            else:
                print('Converting {!s}'.format(f))
                retcode = subprocess.call(["convert", f, fout])
                if retcode != 0:
                    print('failed to convert {!s}. Moving on...'.format(f))
                    continue
                else:
                    print('successfully converted ' \
                            '{!s} to {!s}'.format(f, fout))
    print "Done!"

if __name__ == '__main__':
    sys.exit(main())
