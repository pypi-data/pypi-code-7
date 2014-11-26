# -*- coding: utf-8 -*-

from lar import *
from scipy import *
import json
# import scipy
import numpy as np
# import time as tm
# import gc
# from pngstack2array3d import *
import struct
import getopt
import traceback
#
import matplotlib.pyplot as plt
# threading
import multiprocessing
from multiprocessing import Process, Value, Lock
from Queue import Queue
# cython stuf. not used now
import pyximport; pyximport.install()
import calc_chains_helper as cch


import logging
logger = logging.getLogger(__name__)
# ---------------mjirik

# import funkcí z jiného adresáře
import sys
import os.path

path_to_script = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(path_to_script, "../../../lisa/src"))
from io3d import datareader
# ------------------------------------------------------------
# Logging & Timer
# ------------------------------------------------------------

logging_level = 2

# 0 = no_logging
# 1 = few details
# 2 = many details
# 3 = many many details


def log(n, l):
    if __name__ == "__main__" and n <= logging_level:
        for s in l:
            print "Log:", s

# ------------------------------------------------------------
# Configuration parameters
# ------------------------------------------------------------

PNG_EXTENSION = ".png"
BIN_EXTENSION = ".bin"

# ------------------------------------------------------------
# Utility toolbox
# ------------------------------------------------------------


def invertIndex(nx, ny, nz):
    nx, ny, nz = nx+1, ny+1, nz+1

    def invertIndex0(offset):
        a0, b0 = offset / nx, offset % nx
        a1, b1 = a0 / ny, a0 % ny
        a2, b2 = a1 / nz, a1 % nz
        return b0, b1, b2
    return invertIndex0


def countFilesInADir(directory):
    return len(os.walk(directory).next()[2])


def isArrayEmpty(arr):
    return all(e == 0 for e in arr)


def writeOffsetToFile(file, offsetCurr):
    file.write(struct.pack('>I', offsetCurr[0]))
    file.write(struct.pack('>I', offsetCurr[1]))
    file.write(struct.pack('>I', offsetCurr[2]))


def writeDataToFile(fileToWrite, offsetCurr, objectBoundaryChain):
    writeOffsetToFile(
        fileToWrite,
        offsetCurr    )

    databytes = np.array(objectBoundaryChain.toarray().astype('b').flatten())
    fileToWrite.write( bytearray(databytes))


def read_pkl_by_block(datap, startImage, endImage, centroidsCalc):
    segmentation = datap['segmentation'][startImage:endImage:, :, :]
    # print np.unique(segmentation)
    # segmentation = datap['segmentation'][startImage:endImage, ::5, ::5]
    # segmentation[:10,:15,:20]=2
    # segmentation[:05,:10,:15]=1
# switch colors
    # segmentation[segmentation==wanted_label] = 24
    # segmentation[segmentation!=wanted_label] = 1
    # segmentation[segmentation==2] = 24
    # segmentation[segmentation2] = 1
    # segmentation[segmentation==24] = 0
    # segmentation = (segmentation == wanted_label).astype(np.uint8)
    # print segmentation==2
    # print 'suniq ', np.unique(segmentation)
    # theColors=np.array([[0, 1]])
    return segmentation


def computeChainsThread(
    startImage, endImage, imageHeight, imageWidth,
    imageDx, imageDy, imageDz,
    Nx, Ny, Nz,
    calculateout, BORDER_FILE,
    centroidsCalc, colorIdx, datap, DIR_O
):
    # centroidsCalc - remove
    # @TODO use centroidsCalc
    # print 'cC '
    # print centroidsCalc

    # centroidsCalc = np.array([[0],[ 1]])
    log(2, [ "Working task: " + str(startImage) + "-" + str(endImage) + " [" +
            str( imageHeight) + "-" + str( imageWidth ) + "-" + str(imageDx) +
            "-" + str( imageDy) + "-" + str (imageDz) + "]" ])

    bordo3 = None
    if (calculateout == True):
            with open(BORDER_FILE, "r") as file:
                    bordo3_json = json.load(file)
                    ROWCOUNT = bordo3_json['ROWCOUNT']
                    COLCOUNT = bordo3_json['COLCOUNT']
                    ROW = np.asarray(bordo3_json['ROW'], dtype=np.int32)
                    COL = np.asarray(bordo3_json['COL'], dtype=np.int32)
                    if np.isscalar(bordo3_json['DATA']):
                        # in special case, when all numbers are same
                        logger.debug('bordermatrix data stored as scalar 1')
                        DATA = np.ones(COL.shape, dtype=np.int8) *\
                            np.int8(bordo3_json['DATA'])
                    else:
                        # this is general form
                        logger.debug(
                            'bordermatrix data stored in general form')
                        DATA = np.asarray(bordo3_json['DATA'], dtype=np.int8)
                    # print "border m ",  ROW.shape, COL.shape, DATA.shape
                    # print  "55555555555555555555555555555555555555"
                    bordo3 = csr_matrix(
                        (DATA, COL, ROW), shape=(ROWCOUNT, COLCOUNT))

    xEnd, yEnd = 0, 0
    beginImageStack = 0
# @TODO do something with the input colorNumber
    saveTheColors = centroidsCalc
    # saveTheColors = np.array([1,0])
    saveTheColors = np.array(
        sorted(saveTheColors.reshape(1, len(centroidsCalc))[0]), dtype=np.int
    )

    fileName = "pselettori-"
    if (calculateout == True):
            fileName = "poutput-"
    fileName = fileName + str(startImage) + "_" + str(endImage) + "-"

    returnProcess = 0

    try:
        fullfilename = DIR_O + '/' +\
            fileName + str(saveTheColors[colorIdx]) + BIN_EXTENSION
        logger.debug("file to write " + fullfilename)
        fileToWrite = open(fullfilename, "wb")
        try:
            log(2, ["Working task: " +
                    str(startImage) + "-" +
                    str(endImage) + " [loading colors]"])
            # theImage,colorNumber,theColors = pngstack2array3d(
            #        imageDir, startImage, endImage, colorNumber,
            #        pixelCalc, centroidsCalc)

            # imageDirPkl = "data.pklz"
# -------------------------------

            theImage = read_pkl_by_block(
                datap,
                startImage, endImage,
                centroidsCalc)
            # colorIdx = 2
            # print "orig shape ", datap['segmentation'].shape
            # print "png stack"
            # print 'startim ', startImage
            # print 'endim', endImage
            # print 'unique', np.unique(theImage)
            # print 'centrCol ', centroidsCalc
            # print 'saveTheColors ', saveTheColors, colorIdx
            # print 'calculateout ', calculateout
            # import ipdb; ipdb.set_trace() #  noqa BREAKPOINT
            # theColors = theColors.reshape(1,colorNumber)
            # if (sorted(theColors[0]) != saveTheColors):
            #    log(1, [ "Error: colorNumber have changed"] )
            #    sys.exit(2)

            log(2, ["Working task: " +
                    str(startImage) + "-" +
                    str(endImage) + " [comp loop]" ])
            for xBlock in xrange(imageHeight / imageDx):
                for yBlock in xrange(imageWidth/imageDy):
                    xStart, yStart = xBlock * imageDx, yBlock * imageDy
                    xEnd, yEnd = xStart+imageDx, yStart+imageDy

                    image = theImage[:, xStart:xEnd, yStart:yEnd]
                    # print "image ", image
                    nz, nx, ny = image.shape

                    # Compute a quotient complex of chains with constant field
                    # ------------------------------------------------------------

                    chains3D_old = []
                    chains3D = None
                    hasSomeOne = False
                    if (calculateout != True):
                        chains3D = np.zeros(nx * ny * nz, dtype=np.int32)

                    zStart = startImage - beginImageStack

                    if (calculateout == True):
                        chains3D_old = cch.setList(
                            nx, ny, nz, colorIdx, image, saveTheColors)
                    else:
                        hasSomeOne, chains3D = cch.setListNP(
                            nx, ny, nz, colorIdx, image, saveTheColors)


                    # Compute the boundary complex of the quotient cell
                    objectBoundaryChain = None
                    if (calculateout == True) and (len(chains3D_old) > 0):
                        objectBoundaryChain = larBoundaryChain(
                            bordo3, chains3D_old)

                    # print objectBoundaryChain
                    # brd = bordo3.todense()
                    # print "chains3D_old"
                    # print chains3D_old
                    # print len(chains3D_old)
                    # print "objectBoundaryChain s",
                    # if objectBoundaryChain is not None:
                    #     # print objectBoundaryChain
                    #     print "e ", objectBoundaryChain.todense().shape
                    #     print objectBoundaryChain.toarray().astype('b').flatten()
                    # Save
                    if (calculateout == True):
                        if (objectBoundaryChain != None):
                            writeDataToFile(
                                fileToWrite,
                                np.array(
                                    [zStart, xStart, yStart], dtype=int32),
                                objectBoundaryChain)
                    else:
                        if (hasSomeOne != False):
                            writeOffsetToFile(
                                fileToWrite,
                                np.array([zStart, xStart, yStart], dtype=int32)
                            )
                            fileToWrite.write(
                                bytearray(np.array(
                                    chains3D, dtype=np.dtype('b'))))
        except:
            import traceback
            logger.debug(traceback.format_exc())
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(
                exc_type, exc_value, exc_traceback)
            # Log it or whatever here
            log(1, ["Error: " + ''.join('!! ' + line for line in lines)])
            returnProcess = 2
        finally:
            fileToWrite.close()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        log(1, ["Error: " + ''.join('!! ' + line for line in lines)])
        returnProcess = 2

    return returnProcess

processRes = []


def collectResult(resData):
    processRes.append(resData)


def startComputeChains(
    imageHeight, imageWidth, imageDepth,
    imageDx, imageDy, imageDz,
    Nx, Ny, Nz, calculateout, BORDER_FILE,
    centroidsCalc, colorIdx, datap, DIR_O
):

    beginImageStack = 0
    endImage = beginImageStack

    saveTheColors = centroidsCalc
    log(2, [centroidsCalc])
    saveTheColors = np.array(
        sorted(saveTheColors.reshape(1, len(centroidsCalc))[0]), dtype=np.int)
    log(2, [saveTheColors])
    # print str(imageHeight) + '-' + str(imageWidth) + '-' + str(imageDepth)
    # print str(imageDx) + '-' + str(imageDy) + '-' + str(imageDz)
    # print str(Nx) + '-' + str(Ny) + '-' + str(Nz)
    returnValue = 2

    processPool = max(1, multiprocessing.cpu_count() / 2)
    log(2, ["Starting pool with: " + str(processPool)])

    try:
        pool = multiprocessing.Pool(processPool)
        log(2, ['Start pool'])

        for j in xrange(imageDepth / imageDz):
            startImage = endImage
            endImage = startImage + imageDz
            log(2, [ "Added task: " + str(j) + " -- (" + str(startImage) + "," + str(endImage) + ")" ])

            pool.apply_async(
                            computeChainsThread,
                            args = (startImage, endImage, imageHeight, imageWidth,
                                imageDx, imageDy, imageDz, Nx, Ny, Nz, calculateout,
                                BORDER_FILE, centroidsCalc,
                                colorIdx, datap, DIR_O, ),
                            callback = collectResult)

        log(2, [ "Waiting for completion..." ])
        pool.close()
        pool.join()

        log(1, [ "Completed: " + str(processRes) ])
        if (sum(processRes) == 0):
            returnValue = 0
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        log(1, [ "Error: " + ''.join('!! ' + line for line in lines) ])  # Log it or whatever here

    return returnValue


def segmentation_from_data3d(datap, label):

    datap['segmentation'] = (datap['data3d'] > label).astype(np.uint8) * 2
    # datap['segmentation'][:30,:30,:30] = 1


    return datap


def runComputation(imageDx, imageDy, imageDz, coloridx, calculateout,
    V, FV, input_pkl_file, BORDER_FILE, DIR_O, label):

    dr = datareader.DataReader()
    datap = dr.Get3DData(input_pkl_file, qt_app=None, dataplus_format=True,
                            gui=False)
    if 'segmentation' not in datap.keys():
        datap = segmentation_from_data3d(datap, label)
    segmentation = datap['segmentation'].astype(np.uint8)

    # segmentation = datap['segmentation'][::5,::5,::5]
    # segmentation = datap['segmentation'][300:330,300:350,300:350]
    # datap['segmentation'] = (segmentation ==  1).astype(np.uint8)
    # import ipdb; ipdb.set_trace() #  noqa BREAKPOINT
    # hack kvuli barvam
    segmentation[0, 0, 0] = 0
    segmentation[0, 0, 1] = 1
    datap['segmentation'] = segmentation
    logger.debug("unique %s " %(str(np.unique(datap['segmentation']))))
    imageHeight, imageWidth = datap['segmentation'][:,:,:].shape[1:3]
    # getImageData(INPUT_DIR+str(BEST_IMAGE)+PNG_EXTENSION)
    # imageDepth = countFilesInADir(INPUT_DIR)
    imageDepth = datap['segmentation'].shape[0]
    Nx, Ny, Nz = imageHeight/imageDx, imageWidth/imageDx, imageDepth/imageDz
    returnValue = 2

    try:
        # pixelCalc, centroidsCalc = centroidcalc(INPUT_DIR, BEST_IMAGE, colors)
                # centroidsCalc = np.array([0, 1])
        centroidsCalc = np.unique(datap['segmentation'])
        returnValue = startComputeChains(
                        imageHeight, imageWidth, imageDepth,
                        imageDx, imageDy, imageDz, Nx, Ny, Nz,
                        calculateout, BORDER_FILE,
                        centroidsCalc, coloridx,
                        datap, DIR_O)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        log(1, [ "Error: " + ''.join('!! ' + line for line in lines) ])  # Log it or whatever here
        returnValue = 2
        tracert.print_exc()

    return returnValue

def main(argv):
    ARGS_STRING = 'Args: -r -b <borderfile> -x <borderX> -y <borderY> -z <borderZ> -i <inputdirectory> -c <colors> -d <coloridx> -o <outputdir> -q <bestimage>'

    try:
        opts, args = getopt.getopt(argv, "rb:x:y:z:i:c:d:o:q:")
    except getopt.GetoptError:
        print ARGS_STRING
        sys.exit(2)

    nx = ny = nz = imageDx = imageDy = imageDz = 64
    colors = 2
    coloridx = 0

    mandatory = 5
    calculateout = False
    # Files
    BORDER_FILE = 'bordo3.json'
    BEST_IMAGE = ''
    DIR_IN = ''
    DIR_O = ''

    for opt, arg in opts:
        if opt == '-x':
            nx = ny = nz = imageDx = imageDy = imageDz = int(arg)
            mandatory = mandatory - 1
        elif opt == '-y':
            ny = nz = imageDy = imageDz = int(arg)
        elif opt == '-z':
            nz = imageDz = int(arg)
        elif opt == '-r':
            calculateout = True
        elif opt == '-i':
            DIR_IN = arg + '/'
            mandatory = mandatory - 1
        elif opt == '-b':
            BORDER_FILE = arg
            mandatory = mandatory - 1
        elif opt == '-o':
            mandatory = mandatory - 1
            DIR_O = arg
        elif opt == '-c':
            # mandatory = mandatory - 1
            colors = int(arg)
        elif opt == '-d':
            mandatory = mandatory - 1
            coloridx = int(arg)
        elif opt == '-q':
            BEST_IMAGE = int(arg)
            # BEST_IMAGE = 10

    if mandatory != 0:
        print 'Not all arguments where given'
        print ARGS_STRING
        sys.exit(2)

    returnValue = calcchains_main(
        nx, ny, nz,
        calculateout,
        DIR_IN,
        BORDER_FILE,
        DIR_O,
        # colors,
        coloridx,
        threshold=5000
        )

    sys.exit(returnValue)

def calcchains_main(
    nx, ny, nz,
    calculateout,
    input_filename,
    BORDER_FILE,
    DIR_O,
    # colors,
    coloridx,
    label
):
    # if (coloridx >= colors):
    #     print 'Not all arguments where given (coloridx >= colors)'
    #     print ARGS_STRING
    #     sys.exit(2)

    def ind(x, y, z):
        return x + (nx+1) * (y + (ny+1) * (z))

    chunksize = nx * ny + nx * nz + ny * nz + 3 * nx * ny * nz
    V = [[x, y, z]
         for z in xrange(nz + 1)
         for y in xrange(ny + 1)
         for x in xrange(nx + 1)]

    v2coords = invertIndex(nx, ny, nz)

    # mj
    # construction of vertex grid
    FV = []
    for h in xrange(len(V)):
        x, y, z = v2coords(h)
        if (x < nx) and (y < ny):
            FV.append([h, ind(x+1, y, z), ind(x, y+1, z), ind(x+1, y+1, z)])
        if (x < nx) and (z < nz):
            FV.append([h, ind(x+1, y, z), ind(x, y, z+1), ind(x+1, y, z+1)])
        if (y < ny) and (z < nz):
            FV.append([h, ind(x, y+1, z), ind(x, y, z+1), ind(x, y+1, z+1)])

    # print 'coloridx ', coloridx
    # print 'calc', calculateout
    # print 'V.len: ', len(V), ' V[0:4]: ', V[0:4]
    # print 'FV.len: ', len(FV), 'FV[0:4]: ', FV[0:4]
    # print 'dirl', input_filename, BORDER_FILE
    # print 'diro ', DIR_O

    return runComputation(nx, ny, nz, coloridx, calculateout, V, FV, input_filename,
                   BORDER_FILE, DIR_O, label)

if __name__ == "__main__":
    main(sys.argv[1:])
