#! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import argparse

# import time
import pickle

import sys
import os
# """ import modules from lar-cc/lib """
# sys.path.insert(0, os.path.expanduser('~/projects/lar-cc/lib/py'))
# sys.path.insert(0, '/home/mjirik/projects/lar-cc/lib/py')

import import_library as il
lib_path = il.find_library_path("larcc", "larcc.py")
sys.path.append(lib_path)
from larcc import * # noqa


# input of test file nrn100.py (with definetion of V and FV)
# V = vertex coordinates
# FV = lists of vertex indices of every face (1-based, as required by pyplasm)
#
# sys.path.insert(1, '/Users/paoluzzi/Documents/RICERCA/pilsen/ricerca/')
# from nrn100 import *


def writeFile(filename, vertexes, faces, ftype='auto', shift_obj=True,
              ignore_empty_vertex_warning=False):
    """
    filename
    vertexes
    faces
    """
    if ftype == 'auto':
        _, ext = os.path.splitext(filename)
        ftype = ext[1:]

    if ftype in ('pkl', 'pickle', 'p'):
        pickle.dump([vertexes, faces], open(filename, 'wb'))
    elif ftype == 'obj':
        if shift_obj:
            faces = (np.asarray(faces) + 1).tolist()
        with open(filename, "w") as f:
            for i, vertex in enumerate(vertexes):
                __writeVertexLineToObjFile(f, vertex,
                                           ignore_empty_vertex_warning)
                    # import ipdb; ipdb.set_trace() #  noqa BREAKPOINT

            for face in faces:
                fstr = "f"
                for i in range(0, len(face)):
                    fstr += " %i" % (face[i])

                fstr += "\n"

                f.write(fstr)


def __writeVertexLineToObjFile(f, vertex, ignore_empty_vertex_warning):
    try:
        f.write("v %s %s %s\n" % (
            str(vertex[0]),
            str(vertex[1]),
            str(vertex[2])
        ))
    except IndexError:
        if not ignore_empty_vertex_warning:
            logger.warning('empty vertex %i ' % (i))
        f.write("v 0 0 0\n")


def readFile(filename, ftype='auto', shift_obj=True):
    if not os.path.isfile(filename):
        logger.error('File "%s" not found' % (filename))
        exit(2)
    if ftype == 'auto':
        _, ext = os.path.splitext(filename)
        ftype = ext[1:]

    if ftype in ('pkl', 'pickle', 'p'):
        fdata = pickle.load(open(filename, "rb"))
        vertexes, faces = fdata
    elif ftype == 'obj':
        with open(filename, "r") as f:
            vertexes, faces = __readObjStream(f)
        if shift_obj:
            faces = (np.asarray(faces) - 1).tolist()

    return vertexes, faces


def __readObjStream(f):
    vertexes = []
    faces = []
    for line in f.readlines():
        lnarr = line.strip().split(' ')
        if lnarr[0] == 'v':
            try:
                vertex = [
                    int(lnarr[1]),
                    int(lnarr[2]),
                    int(lnarr[3])
                ]
            except ValueError:
                vertex = [
                    float(lnarr[1]),
                    float(lnarr[2]),
                    float(lnarr[3])
                ]

            vertexes.append(vertex)
        elif lnarr[0] == 'f':
            face = [0] * (len(lnarr) - 1)
            for i in range(1, len(lnarr)):
                face[i - 1] = int(lnarr[i])
            faces.append(face)

    return vertexes, faces


def main():

    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # logger.debug('input params')

    # input parser
    parser = argparse.ArgumentParser(
        description="Laplacian smoothing"
    )
    parser.add_argument(
        '-i', '--inputfile',
        default=None,
        required=True,
        help='input file'
    )
    parser.add_argument(
        '-o', '--outputfile',
        default='smooth.obj',
        help='input file'
    )
    parser.add_argument(
        '-mib', '--moveindexbasis',
        type=int,
        default=0,
        help='indexes are 0-based or 1-based')
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    parser.add_argument(
        '--console', action='store_true',
        help='Debug mode')

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    # t0 = time.time()
    V, FV = readFile(args.inputfile)
    logger.info("Data readed from '%s'" % (args.inputfile))
    if args.moveindexbasis is not 0:
        FV = (np.array(FV) + args.moveindexbasis).tolist()

    if args.console:
        import ipdb; ipdb.set_trace() #  noqa BREAKPOINT

    writeFile(args.outputfile, V, FV)
    logger.info("Data stored to '%s'" % (args.outputfile))

if __name__ == "__main__":
    main()
