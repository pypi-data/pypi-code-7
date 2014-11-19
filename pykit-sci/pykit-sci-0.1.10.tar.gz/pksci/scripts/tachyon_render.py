# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
===============================================================
Render tachyon scenes (:mod:`pksci.scripts.tachyon_render`)
===============================================================

.. currentmodule:: pksci.scripts.tachyon_render

.. autofunction:: tachyon_render

"""
from __future__ import absolute_import, print_function, division

#TODO: create subparsers for output resolution which have different default
#      resolutions but also allow optional args for setting res either
#      completely manually or from a list of choices.

#TODO: implement file database check to test if rendered file exists

import argparse
import os
import shutil
import subprocess
import sys

__all__ = ['tachyon_render']

hdres = {'1280x720': ('1280', '720'),
         '1024x640': ('1024', '640'),
         '1152x720': ('1152', '720'),
         '1280x800': ('1280', '800'),
         '1440x900': ('1440', '900')}
large_hdres = {'1920x1080': ('1920', '1080'),
               '2560x1440': ('2560', '1440')}

sdres = {'400x300': ('400', '300'),
         '800x600': ('800', '600'),
         '1024x768': ('1024', '768'),
         '1600x1200': ('1600', '1200')}
large_sdres = {'3200x2400': ('3200', '2400'),
               '4800x3600': ('4800', '3600')}

squares = {'100x100': ('100', '100'),
           '500x500': ('500', '500'),
           '1000x1000': ('1000', '1000'),
           '2000x2000': ('2000', '2000'),
           '2500x2500': ('2500', '2500')}

large_squares = {'5000x5000': ('5000', '5000')}

master_resmap = dict(hdres.items() + sdres.items() +
                     large_hdres.items() + large_sdres.items() +
                     squares.items() + large_squares.items())

foutext = {'BMP': '.bmp',
           'JPEG': '.jpg',
           'PNG': '.png',
           'PPM': '.ppm',
           'PPM48': '.ppm',
           'PSD48': '.psd',
           'RGB': '.rgb',
           'TARGA': '.tga'}


def tachyon_render(args):
    """Render tachyon scenes.

    Parameters
    ----------
    args : list
        command line argument list

    Returns
    -------
    None

    """
    verbosity = args.verbose
    numthreads = args.numthreads
    overwrite = args.overwrite
    aasamples = args.aasamples
    raydepth = args.raydepth
    skysamples = args.skylight_samples
    shading = '-{}shade'.format(args.shading_quality)
    highlight = '-shade_{}'.format(args.specular_highlight)
    fmt = args.format
    tachyon_bin = args.tachyon_bin

    files = [f for f in args.files if os.path.isfile(f)]
    #if sys.platform == 'win32':
    #    from glob import glob
    #    tachyon_bin = "tachyon_WIN32.exe"
    #    files = glob(files[0])

    fname_suffix = None
    if args.detailed_suffix:
        fname_suffix = '-aasamples={}'.format(aasamples) + \
            ',raydepth={}'.format(raydepth) + \
            ',skysamples={}'.format(skysamples)

    resmap = {}

    reskey_list = args.reskeys
    if reskey_list is None:
        resmap['x'.join(args.res)] = args.res
    else:
        for reskey in reskey_list:
            resmap[reskey] = master_resmap[reskey]

    for f in files:
        for key, res in resmap.iteritems():
            try:
                os.mkdir(key)
            except OSError:
                pass

            fout = os.path.splitext(f)[0]
            if fname_suffix is not None:
                fout += fname_suffix
            fout += foutext[fmt]
            foutpath = os.path.join(key, fout)

            if os.path.isfile(foutpath):
                if overwrite:
                    try:
                        print('overwriting existing file: {}'.format(foutpath))
                        os.remove(foutpath)
                    except OSError:
                        continue
                else:
                    print('{} already exists. Skipping file...'.format(fout))
                    continue

            print('Rendering {}...'.format(f))
            retcode = \
                subprocess.call([tachyon_bin, f, verbosity,
                                 shading, highlight,
                                 '-numthreads', numthreads,
                                 '-raydepth', raydepth,
                                 '-skylight_samples', skysamples,
                                 '-aasamples', aasamples,
                                 '-res', res[0], res[1],
                                 '-format', fmt, '-o', fout])
            if retcode == 0:
                print('successfully rendered {}...'.format(fout))
                shutil.move(fout, key)
            else:
                print('failed to render {}. '.format(f) +
                      'Moving on...')


def _argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--HD1280x720', dest='reskeys',
                        action='append_const', const='1280x720',
                        help='render in 16:9 widescreen @ 1280 x 720')
    parser.add_argument('--HD1920x1080', dest='reskeys',
                        action='append_const', const='1920x1080',
                        help='render in 16:9 widescreen @ 1920 x 1080')
    parser.add_argument('--HD1440x900', dest='reskeys',
                        action='append_const', const='1440x900',
                        help='render in 16:10 widescreen @ 1440 x 900')
    parser.add_argument('--HD1920x1200', dest='reskeys',
                        action='append_const', const='1920x1200',
                        help='render in 16:10 widescreen @ 1920 x 1200')
    parser.add_argument('--SD1600x1200', dest='reskeys',
                        action='append_const', const='1600x1200',
                        help='render in 4:3 standard @ 1600 x 1200')
    parser.add_argument('--SD3200x2400', dest='reskeys',
                        action='append_const', const='3200x2400',
                        help='render in 4:3 standard @ 3200 x 2400')
    parser.add_argument('--square500', dest='reskeys',
                        action='append_const', const='500x500',
                        help='render in 1:1 square @ 500 x 500')
    parser.add_argument('--square1000', dest='reskeys',
                        action='append_const', const='1000x1000',
                        help='render in 1:1 square @ 1000 x 1000')

    parser.add_argument('--res', nargs=2, metavar=('Xres', 'Yres'),
                        default=squares['2000x2000'],
                        help='image size in pixels (default: %(default)s)')

    parser.add_argument('--format', default='PPM48',
                        choices=('BMP', 'PPM', 'PPM48', 'PSD48', 'TARGA'),
                        help='output file format (default: %(default)s)')

    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    parser.add_argument('--numthreads', default='4',
                        help='number of MPI threads to use. '
                        '(default: %(default)s)')
    parser.add_argument('--tachyon-bin', default='tachyon',
                        help='set the name of the tachyon binary executable '
                        '(default: %(default)s)')
    parser.add_argument('--aasamples', default='100',
                        help='maximum supersamples taken per pixel '
                        '(default: %(default)s)')
    parser.add_argument('--raydepth', default='50',
                        help='maximum ray recursion depth '
                        '(default: %(default)s)')
    parser.add_argument('--skylight-samples', default='100',
                        help='number of sample rays to shoot '
                        '(default: %(default)s)')
    parser.add_argument('--shading-quality', default='full',
                        choices=('full', 'medium', 'low', 'lowest'),
                        help='shading quality (default: %(default)s)')
    parser.add_argument('--specular-highlight', default='blinn',
                        choices=('blinn', 'blinn_fast', 'phong', 'nullphong'),
                        help='specular highlight shading options '
                        '(default: %(default)s)')

    parser.add_argument('--detailed-suffix', action='store_true',
                        help='append the tachyon rendering settings '
                        'to the name of the output file')

    parser.add_argument('-v', '--verbose', action='store_const',
                        const='+V', default='-V', help='verbose messages on')

    parser.add_argument('files', nargs='+', help='tachyon scene files')
    return parser


def main():

    args = _argparser().parse_args()
    #tachyon_render(**vars(args))
    tachyon_render(args)

if __name__ == '__main__':
    sys.exit(main())
