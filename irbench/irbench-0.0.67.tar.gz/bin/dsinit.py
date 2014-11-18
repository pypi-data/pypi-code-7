#!/usr/bin/env python
# coding: utf-8

################################################################
# Dataset Builder ##############################################
################################################################

"""
   File Name: dsinit.py
      Author: Wan Ji
      E-mail: wanji@live.com
  Created on: Tue Mar 18 14:07:56 2014 CST
"""
DESCRIPTION = """
"""

import random
import argparse
import irbench.dataset as irds
import numpy as np


def getargs():
    """ Parse program arguments.
    """

    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=
                                     argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='dataset', help='dataset help')
    for (name, cls) in irds.DS_BUILDERS.iteritems():
        ds_parser = subparsers.add_parser(name, help=cls.__doc__)
        print name, cls
        cls.set_parser(ds_parser)
    parser.add_argument('seed', type=int, nargs='?', default=0,
                        help="seed for random number generator")

    return parser.parse_args()


def main(args):
    """ Main entry.
    """

    # to ensure that the generated list is consistent every time
    random.seed(args.seed)
    np.random.seed(args.seed)

    builder = irds.DS_BUILDERS[args.dataset](args)
    builder.generate(args.trg_dir)
    builder.save(args.trg_dir + ".pkl")

if __name__ == '__main__':
    main(getargs())
