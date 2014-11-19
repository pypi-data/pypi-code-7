#!/usr/bin/env python
"""
convert PS files to PDF files

"""

import argparse
import os
import subprocess
import sys

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite', action='store_true',
            help='overwrite existing files')
    parser.add_argument('psfiles', nargs='+', help='postscript files')
    args = parser.parse_args()
    overwrite = args.overwrite
    files = args.psfiles
    for f in files:
        if os.path.isfile(f) and f.lower().endswith('.ps'):
            fout = os.path.splitext(f)[0] + '.pdf'
            if os.path.isfile(fout) and not overwrite:
                print('Skipping {!s} file conversion '.format(f) + \
                        'because {!s} already exists'.format(fout))
                continue
            else:
                print('Converting {!s} to {!s}\n'.format(f, fout))
                retcode = subprocess.call(["ps2pdf", f])
                if retcode != 0:
                    print('command failure\n')
                else:
                    print('command success!\n')

if __name__ == '__main__':
    sys.exit(main())
