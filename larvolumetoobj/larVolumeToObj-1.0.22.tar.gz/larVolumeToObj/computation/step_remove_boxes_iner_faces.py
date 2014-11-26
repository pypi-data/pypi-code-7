#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Generator of histology report

"""

import logging
logger = logging.getLogger(__name__)

import argparse
import sys

import numpy as np
# import traceback
import copy
import time

sys.path.insert(0, './py/computation')
sys.path.insert(0, '../../')
from fileio import readFile, writeFile


def removeFromOneAxis():
    pass


def findBoundaryVertexesForAxis(vertexes, step, axis, isOnBoundary=None):
    """
    Return bool array of same length as is number of vertexes. It is true when
    vertex on same index is on box edge.
    """

    vertexes = np.array(vertexes)
    mx = np.max(vertexes[:, axis])
    mn = np.min(vertexes[:, axis])
    if mn < 0:
        logger.error("minimum is lower then 0")

    box_coordinates = range(0, mx, step)

    vertexes_axis = vertexes[:, axis]
    if isOnBoundary is None:
        isOnBoundary = np.zeros(vertexes_axis.shape, dtype=np.bool)

    for coor in box_coordinates:
        isOnBoundary = isOnBoundary + (vertexes_axis == coor)

    return isOnBoundary


def reindexVertexesInFaces(faces, new_indexes, index_base=0):
    for face in faces:
        try:
            for i in range(0, len(face)):
                face[i] = new_indexes[face[i] - index_base] + index_base
            # face[0] = new_indexes[face[0]-1] + 1
            # face[1] = new_indexes[face[1]-1] + 1
            # face[2] = new_indexes[face[2]-1] + 1
        except:
            import traceback
            traceback.print_exc()
            print 'fc ', face, ' i ', i
            print len(new_indexes)

    return faces


def removeDoubleVertexesAndFaces(vertexes, faces, boxsize=None, index_base=0,
                                 use_dict_algorithm=True):
    """
    Main function of module. Return object description cleand from double
    vertexes and faces.
    """

    t0 = time.time()
    # new_vertexes, inv_vertexes = removeDoubleVertexes(vertexes)
    new_vertexes, inv_vertexes = removeDoubleVertexesAlternative(vertexes)
    t1 = time.time()
    logger.info("Doubled vertex removed          " + str(t1 - t0))
    logger.info("Number of vertexes: %i " % (len(new_vertexes)))
    new_faces = reindexVertexesInFaces(faces, inv_vertexes,
                                       index_base=index_base)
    t2 = time.time()
    logger.info("Vertexes in faces reindexed     " + str(t2 - t1))
    if use_dict_algorithm:
        logger.debug("Using dict algotithm by Alberto")
        new_faces = removeDoubleFacesByAlberto(new_faces)
    else:
        if boxsize is None:
            logger.debug("Using removeDoubleFaces")
            new_faces = removeDoubleFaces(new_faces)
        else:
            logger.debug("Using removeDoubleFacesOnlyOnBoundaryBoxes")
            new_faces = removeDoubleFacesOnlyOnBoundaryBoxes(
                new_vertexes, new_faces, boxsize[0], index_base=index_base)
# @TODO add other axis
    t3 = time.time()
    logger.info("Double faces removed            " + str(t3 - t2))
    return new_vertexes, new_faces


def removeDoubleVertexesAlternative(V):
    """
    alternativte removing of doublefaces. Hopefully more memory efficient
    """
    X = range(len(V))
    # Vs = [v for (v, x) in VIsorted]
    # Is = [x for (v, x) in VIsorted]
    Vs = []
    Is = [0]*len(V)

    prevv = None
    i = 0
    for [v, x] in sorted(zip(V, X)):
        if v == prevv:
            # prev index was increased
            Is[x] = i - 1
        else:
            Vs.append(v)
            Is[x] = i
            i = i + 1
            prevv = v

    return Vs, Is


def removeDoubleVertexes(vertexes):
    """
    Return array of faces with remowed rows of both duplicates
    """
    vertexes = np.array(vertexes)

    b = np.ascontiguousarray(vertexes).view(
        np.dtype((np.void, vertexes.dtype.itemsize * vertexes.shape[1])))
    _, idx, inv = np.unique(b, return_index=True, return_inverse=True)

    unique_vertexes = vertexes[idx]
    return unique_vertexes.tolist(), inv


def removeDoubleFacesOnlyOnBoundaryBoxes(vertexes, faces, bbsize,
                                         index_base=0):
    """
    Faster sister of removeDoubleFaces.

    It works only on box boundary
    """

    on, off = findBoundaryFaces(vertexes, faces, bbsize, index_base)

    # on = range(1, 100)

    off_boundary_faces = np.array(faces)[off]
    on_boundary_faces = np.array(faces)[on]
    new_on_boundary_faces = removeDoubleFaces(on_boundary_faces)
    new_faces = np.concatenate(
        (off_boundary_faces, np.array(new_on_boundary_faces)),
        0)
    return new_faces.tolist()


def removeDoubleFaces(faces):
    """
    Return array of faces with remowed rows of both duplicates
    """
    faces_orig = copy.copy(np.array(faces))
    for face in faces:
        face = face.sort()
    faces = np.array(faces)

    reduced_idx = getIndexesOfSingleFaces(faces)
    # reduced_idx2 = getIndexesOfSingleFacesBlocks(faces)
    # kimport ipdb; ipdb.set_trace() #  noqa BREAKPOINT

    unique_faces = faces_orig[reduced_idx]
    return unique_faces.tolist()


def removeDoubleFacesByAlberto(FW):
    from collections import defaultdict
    # use of Albertos algorithm

    cellDict = defaultdict(list)
    for k, cell in enumerate(FW):
        cellDict[tuple(cell)] += [k]
    FW = [list(key) for key in cellDict.keys() if len(cellDict[key]) == 1]
    return FW


def getIndexesOfSingleFaces(faces):
    """
    Return indexes of not doubled faces.
    """
    b = np.ascontiguousarray(faces).view(
        np.dtype((np.void, faces.dtype.itemsize * faces.shape[1])))
    _, idx, inv = np.unique(b, return_index=True, return_inverse=True)
# now idx describes unique indexes
# but we want remove all duplicated indexes. Not only duplicates
    duplication_number = [np.sum(inv == i) for i in range(0, len(idx))]
    reduced_idx = idx[np.array(duplication_number) == 1]
    return reduced_idx


def getIndexesOfSingleFacesBlocks(faces):
    """
    Return indexes of not doubled faces.

    Function is sister of getIndexesOfSingleFaces. Difference is that
    computataion is performed by blocks
    """
    reduced_bool = np.zeros(faces.shape[0], dtype=np.bool)

    # working with whole list of faces is time consuming
    # this is why we do this in blocks
    block_size = 20
    for i in range(0, faces.shape[0]):
        # select faces with first
        selected = (faces[:, 0] >= i) * (faces[:, 0] < i + block_size)
        faces_subset = faces[selected]

        b = np.ascontiguousarray(faces_subset).view(
            np.dtype((np.void, faces.dtype.itemsize * faces_subset.shape[1])))
        _, idx, inv = np.unique(b, return_index=True, return_inverse=True)
# now idx describes unique indexes
# but we want remove all duplicated indexes. Not only duplicates
        duplication_number = [np.sum(inv == i) for i in range(0, len(idx))]
        subset_reduced_idx = idx[np.array(duplication_number) == 1]

        selected_idx_nz = np.nonzero(selected)
        selected_idx = selected_idx_nz[0]

        # arrange subset to original data
        reduced_bool[selected_idx[subset_reduced_idx]] = True
        reduced_idx = np.nonzero(reduced_bool)[0]
    return reduced_idx


def facesHaveAllPointsInList(faces, isOnBoundaryInds):
    faces = np.array(faces)
# Face has 3 points
    isInVoxelList = np.zeros(faces.shape, dtype=np.bool)
    for vertexInd in isOnBoundaryInds:
        isInVoxelList = isInVoxelList + (faces == vertexInd)

    suma = np.sum(isInVoxelList, 1)
    return suma >= faces.shape[1]


def findBoundaryFaces(vertexes, faces, step, index_base=0):
    """
    vertexes, step
    index_base is 0 or 1. Based on indexing of first vertex
    """

    # faces = np.array(faces)
    # print 'start ', faces.shape
    facesOnBoundary = np.zeros(len(faces), dtype=np.bool)
    for axis in range(0, 3):
        isOnBoundary = findBoundaryVertexesForAxis(
            vertexes, step, axis)
# faces.shape[1]
        isOnBoundaryInds = (np.nonzero(isOnBoundary)[0] + index_base).tolist()
        facesOnBoundary += facesHaveAllPointsInList(faces, isOnBoundaryInds)

    # reduced faces set
    on_boundary = np.nonzero(facesOnBoundary)[0]
    off_boundary = np.nonzero(-facesOnBoundary)[0]
    # faces_new = faces[- facesOnBoundary]
    # print ' faces ', faces_new.shape
    # return vertexes, faces_new.tolist()
    return on_boundary, off_boundary


def main():
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # logger.debug('input params')

    # input parser
    parser = argparse.ArgumentParser(
        description="Remove faces from file"
    )
    parser.add_argument(
        '-i', '--inputfile',
        default=None,
        required=True,
        help='input file'
    )
    parser.add_argument(
        '-o', '--outputfile',
        default=None,
        required=True,
        help='output file'
    )
    parser.add_argument(
        '-b', '--boxsize',
        default=None,
        type=int,
        metavar='N',
        nargs='+',
        help='Size of box'
    )
    parser.add_argument(
        '-a', '--alberto', action='store_true',
        help='Albertos algorithm')
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    v, f = readFile(args.inputfile)
    print "Before"
    print "Number of vertexes: %i    Number of faces %i" % (len(v), len(f))
    # findBoxVertexesForAxis(v, 2, 0)
    # v, f = findBoundaryFaces(v, f, 2)
    v, f = removeDoubleVertexesAndFaces(v, f, args.boxsize,
                                        use_dict_algorithm=args.alberto)
    writeFile(args.outputfile, v, f)
    print "After"
    print "Number of vertexes: %i    Number of faces %i" % (len(v), len(f))

if __name__ == "__main__":
    main()
