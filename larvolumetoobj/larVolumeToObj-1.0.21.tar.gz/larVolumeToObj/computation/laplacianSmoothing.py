#! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import argparse

import time

import sys
# import os
""" import modules from lar-cc/lib """

import import_library as il
lib_path = il.find_library_path("larcc", "larcc.py")
sys.path.append(lib_path)
from larcc import *  # noqa

from fileio import writeFile, readFile


def triangulateSquares(F,
                       a=[0, 1, 2], b=[2, 3, 0],
                       c=[1, 0, 2], d=[3, 2, 0]
                       ):
    """
    Convert squares to triangles
    """
    FT = []
    for face in F:
        FT.append([face[a[0]], face[a[1]], face[a[2]]])
        FT.append([face[b[0]], face[b[1]], face[b[2]]])
        # FT.append([face[c[0]], face[c[1]], face[c[2]]])
        # FT.append([face[d[0]], face[d[1]], face[d[2]]])
        # FT.append([face[0], face[3], face[2]])
    return FT


# scipy.sparse matrices required
# Computation of Vertex-to-vertex adjacency matrix
#


def adjacencyQuery(V, FV):
    # dim = len(V[0])
    csrFV = csrCreate(FV)
    csrAdj = matrixProduct(csrTranspose(csrFV), csrFV)
    return csrAdj


def adjacencyQuery0(dim, csrAdj, cell):
    nverts = 4
    cellAdjacencies = csrAdj.indices[
        csrAdj.indptr[cell]:csrAdj.indptr[cell + 1]]
    return [
        acell
        for acell in cellAdjacencies
        if dim <= csrAdj[cell, acell] < nverts
    ]


# construction of the adjacency graph of vertices
# returns VV = adjacency lists (list of indices of vertices
# adjacent to a vertex) of vertices
#
def adjVerts(V, FV):
    n = len(V)
    VV = []
    V2V = adjacencyQuery(V, FV)
    V2V = V2V.tocsr()
    for i in range(n):
        dataBuffer = V2V[i].tocoo().data
        colBuffer = V2V[i].tocoo().col
        row = []
        for val, j in zip(dataBuffer, colBuffer):
            if val == 2:
                row += [int(j)]
        VV += [row]
    return VV


def makeSmoothing(V, FV):
    """
    deprecated version of algorithm
    """
    # t1 = time.time()
    # csrAdj = adjacencyQuery(V, FV)
    # t2 = time.time()
    # logger.info('Adjency query                   %ss' %
    #             (str(t2 - t1)))

# transformation of FV to 0-based indices (as required by LAR)
    # FV = [[v - 1 for v in face] for face in FV]
    # t3 = time.time()
    # logger.info('FV transformation               %ss' %
    # (str(t3 - t2)))

    if False:
        # if args.visualization:
        VIEW(STRUCT(MKPOLS((V, FV))))
        VIEW(EXPLODE(1.2, 1.2, 1.2)(MKPOLS((V, FV))))

    t4 = time.time()
    VV = adjVerts(V, FV)
    t5 = time.time()
    logger.info('adj verts                       %ss' %
                (str(t5 - t4)))
# VIEW(STRUCT(MKPOLS((V,CAT([DISTR([VV[v],v ]) for v in range(n)]))))) #
# long time to evaluate

# Iterative Laplacian smoothing
# input V = initial positions of vertices
# output V1 = new positions of vertices
#
    V1 = AA(CCOMB)([[V[v] for v in adjs] for adjs in VV])

    t6 = time.time()
    logger.info('1st iteration                   %ss' %
                (str(t6 - t5)))
# input V1
# output V2 = new positions of vertices
#
    V2 = AA(CCOMB)([[V1[v] for v in adjs] for adjs in VV])
    t7 = time.time()
    logger.info('2st iteration                   %ss' %
                (str(t7 - t6)))

# move index basis back
    # FV = (np.array(FV) + 1).tolist()

    return V2


def ccomb(box):
    minVert, maxVert = box
    coordPair = zip(minVert, maxVert)

    def ccomb0((p, vectors)):
        theSum = VECTSUM(vectors)
        num = float(len(vectors))
        for i in range(3):
            for coord in coordPair[i]:
                if p[i] == coord:
                    if theSum != []:
                        theSum[i] = num * coord
        return (sp.array(theSum) / num).tolist()
    return ccomb0


def iterativeLaplacianSmoothing(V, FV, iterations=1):
    # Iterative Laplacian smoothing
    # input V = initial positions of vertices
    # output V1 = new positions of vertices
    #

    # V1 = AA(CCOMB)([[V[v] for v in adjs] for adjs in  VV])
    VV = adjVerts(V, FV)
    box = (V[0], V[-1])
    for i in range(0, iterations):
        V = AA(ccomb(box))(
            [(V[k], [V[v] for v in adjs]) for k, adjs in enumerate(VV)]
        )
    return V
    # VIEW(STRUCT(MKPOLS((V1, FV))))


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
        '-v', '--visualization', action='store_true',
        help='Use visualization')
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    t0 = time.time()
    V, FV = readFile(args.inputfile)

    t1 = time.time()
    logger.info('Data imported                   %ss. #V: %i, #FV: %i' %
                (str(t1 - t0), len(V), len(FV)))

    # V2 = makeSmoothing(V, FV)
    V2 = iterativeLaplacianSmoothing(V, FV)

    if args.visualization:
        # t7 = time.time()
        # FV = triangulateSquares(FV)
        # tv1 = time.time()
        # logger.info('triangulation               %ss' %
        #             (str(tv1 - t7)))
        VIEW(STRUCT(MKPOLS((V2, FV))))

# write outputs
    writeFile(args.outputfile + '.pkl', V2, FV)
    writeFile(args.outputfile, V2, FV)
    logger.info("Data stored to ' %s" % (args.outputfile))

if __name__ == "__main__":
    main()
