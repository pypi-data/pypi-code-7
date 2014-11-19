# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
==============================================================
Timestamp frames (:mod:`pksci.scripts.timestamp_frames`)
==============================================================

.. currentmodule:: pksci.scripts.timestamp_frames

.. autofunction:: timestamp_frames

"""
from __future__ import absolute_import, division, print_function

import argparse
import os
import subprocess
import sys

from ..tools import get_fpath

__all__ = ['timestamp_frames']


#def conversion_factor(units):
#    unit_conversions = {'ps': 'ps2fs'}
#    conversion_factors = {'ps2fs': 1e-3}
#    cf = conversion_factors[unit_conversions[units]]
#    return cf

def timestamp_frames(image_frames, color='black', x=50, y=100, ptsize=72,
                     fuzzfactor=10, timestep=0.0005, timesteps_per_frame=10,
                     timestep_units='ps', overwrite=False,
                     outpath=os.getcwd(), timestamp_precision=2):
    """Timestamp frames of molecular dynamics trajectory output.


    Parameters
    ----------
    images_frames : sequence
    color : str, optional
        text color
    x, y : float, optional
    ptsize : int, optional
    fuzzfactor : float, optional
    timestep : float, optional
    timesteps_per_frame : int, optional
    timestep_units : str, optional
    overwrite : bool, optional
    outpath : str, optional

    """
    failed_once = False

    for f in image_frames:
        if os.path.isfile(f):
            print(u'processing file: {}'.format(f))
            fname_root = os.path.splitext(f)[0]
            prefix = ''
            try:
                prefix = fname_root.split('-')[0]
                frame = int(fname_root.split('-')[-1])
            except ValueError:
                try:
                    prefix = fname_root.split('.')[0]
                    frame = int(fname_root.split('.')[-1].lstrip('0'))
                except ValueError:
                    print("Unable to determine frame number from file name.")
                    if failed_once:
                        frame += 1
                    else:
                        frame = 0
                        failed_once = True
            #fout = prefix + '-' + str(frame).zfill(5) + \
            #        '_fuzzfactor={}'.format(fuzzfactor) + '_timestamped.png'
            fout = prefix + '-' + str(frame).zfill(5) + '_timestamped.png'

            fout = get_fpath(fname=fout, outpath=outpath, overwrite=overwrite,
                             add_fnum=False, verbose=True)

            convert_cmd = ["convert"]
            convert_cmd.append("-fuzz")
            convert_cmd.append("{}".format(fuzzfactor))
            convert_cmd.append("-transparent")
            convert_cmd.append("white")
            convert_cmd.append("-font")
            convert_cmd.append("Arial")
            convert_cmd.append("-fill")
            convert_cmd.append(color)
            convert_cmd.append("-pointsize")
            convert_cmd.append("{!s}".format(ptsize))

            if os.path.isfile(fout):
                print('Skipping file...')
                continue
            else:
                frame_ts = frame * timestep * timesteps_per_frame
                #if not units == 'fs':
                    #frame_ts = frame_ts * conversion_factor(units)
                ts_format = '{:.' + str(timestamp_precision) + 'f}'
                timestamp = "text {},{} 't = {} {}'".format(
                    x, y, ts_format.format(frame_ts), timestep_units)
                print('timestamping {}...'.format(f))

                convert_cmd.append("-draw")
                convert_cmd.append(timestamp)
                convert_cmd.append("-shave")
                shave_geometry = "50x25"
                #shave_geometry = "10x10"
                convert_cmd.append(shave_geometry)
                convert_cmd.append(f)
                convert_cmd.append(fout)

                retcode = subprocess.call(convert_cmd)
                #retcode = subprocess.call(["convert",
                #    "-fuzz", '{}'.format(fuzzfactor),
                #    "-transparent", "white",
                #    "-font", "Arial",
                #    "-fill", color,
                #    "-pointsize", '{!s}'.format(ptsize),
                #    "-draw", timestamp,
                #    "-shave", '{}'.format(shave_geometry),
                #    f, fout])
                if retcode != 0:
                    print('failed to timestamp {}'.format(f))
                    print('moving on...')
                    continue
                else:
                    print('successfully timestamped {}'.format(f))


def _argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', default='black',
                        help='text color (default: %(default)s)')
    parser.add_argument('--timestep', type=float, default=0.0005,
                        help='molecular dynamics timestep '
                        '(default: %(default)s)')
    parser.add_argument('--timestep-units', default='ps',
                        help='timestep units (default: %(default)s)')
    parser.add_argument('--timesteps-per-frame', type=int, default=10,
                        help='number of timesteps between frame dumps '
                        '(default: %(default)s)')
    parser.add_argument('--x', type=int, default=50,
                        help='x pos (default: %(default)s)')
    parser.add_argument('--y', type=int, default=100,
                        help='y pos (default: %(default)s)')
    parser.add_argument('--fuzzfactor', type=float, default=10,
                        help='percent fuzz factor for converting color to '
                        'alpha (default: %(default)s)')
    parser.add_argument('--ptsize', type=int, default=72,
                        help='pointsize (default: %(default)s)')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite existing files')
    parser.add_argument('--outpath', default=os.getcwd(),
                        help='set output path (default: %(default)s)')
    parser.add_argument('--timestamp-precision', type=int, default=2,
                        help='precision of timestamp (default: %(default)s)')
    parser.add_argument('image_frames', nargs='+',
                        help='image frames')
    return parser


def main():
    args = _argparser().parse_args()
    timestamp_frames(**vars(args))

if __name__ == '__main__':
    sys.exit(main())
