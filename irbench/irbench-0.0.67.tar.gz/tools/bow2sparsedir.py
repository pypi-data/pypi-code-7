#!/usr/bin/env python
# coding: utf-8

#########################################################################
#########################################################################

"""
   File Name: bow2sparse.py
      Author: Wan Ji
      E-mail: wanji@live.com
  Created on: Mon Mar 24 11:33:07 2014 CST
"""
DESCRIPTION = """
This program is used for converting the BoW features from SVM format to
sparse matrix format in numpy.
"""

import os
import sys
import argparse
import multiprocessing


import numpy as np
from scipy.sparse import lil_matrix


def perr(msg):
    """ Print error message.
    """

    sys.stderr.write("%s" % msg)
    sys.stderr.flush()


def pinfo(msg):
    """ Print information message.
    """

    sys.stdout.write("%s" % msg)
    sys.stdout.flush()


def runcmd(cmd):
    """ Run command.
    """

    perr("%s\n" % cmd)
    os.system(cmd)


def getargs():
    """ Parse program arguments.
    """

    parser = argparse.ArgumentParser(
        description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('svmpath', type=str,
                        help='input: features in SVM format')
    parser.add_argument('npydir', type=str,
                        help='output: features in NPY format')
    parser.add_argument('rows', type=int,
                        help='number of rows')
    parser.add_argument('cols', type=int,
                        help='number of cols')
    parser.add_argument('-t', '--dtype', type=str, nargs='?',
                        default='float32',
                        help='data type')
    parser.add_argument('-b', '--blksz', type=int, nargs='?', default=12800,
                        help='block size')
    parser.add_argument('-c', '--ncpu', type=int, nargs='?',
                        default=multiprocessing.cpu_count(),
                        help='pool size (number of CPUs)')

    return parser.parse_args()


def proc_convert(v_par):
    """ proc
    """
    rid = v_par[0]
    line = v_par[1]
    dtype = v_par[2]
    items = [item.split(":") for item in line.split()[1:]]
    return (rid,
            [int(item[0]) for item in items],
            [dtype(item[1]) for item in items])


def main(args):
    """ Main entry.
    """

    dtype = eval('np.%s' % args.dtype)
    runcmd("mkdir -p %s" % args.npydir)

    pool = multiprocessing.Pool(processes=args.ncpu)
    pinfo("Converting ...\n")
    with open(args.svmpath) as svmf:
        for i in range(0, args.rows, args.blksz):
            nrows = min(args.blksz, args.rows - i)
            parlst = [(j, svmf.readline(), dtype) for j in range(nrows)]

            pinfo("\tInitializing matrix ... ")
            feat = lil_matrix((nrows, args.cols), dtype=dtype)
            pinfo("Done!\n")

            for rid, res in enumerate(pool.imap_unordered(proc_convert,
                                                          parlst)):
                if (rid % 100) == 0:
                    pinfo("\r\t%d/%d" % (i+rid, args.rows))
                feat.rows[res[0]] = res[1]
                feat.data[res[0]] = res[2]
            pinfo("\r\t%d/%d" % (i+nrows, args.rows))

            pinfo("\tConverting to csr_matrix ... ")
            feat = feat.tocsr()
            pinfo("Done!\n")

            pinfo("\tDumping ... ")
            npypath = os.path.sep.join([args.npydir,
                                        "bow_%d" % (i / args.blksz)])
            np.save(npypath, (feat.data, feat.nonzero()))
            pinfo("Done!\n")

    pinfo("\r\t%d/%d\tDone!\n" % (args.rows, args.rows))


if __name__ == '__main__':
    main(getargs())
