from __future__ import division
import numpy

from fieldpy.primitives.idx import idx2D, idx3D
from fieldpy.primitives.datafield import datafield2D, datafield3D

class gammaCalculator2D(object):
    r"""

    """

    def __init__(self, dfRef, dfEval):
        r"""

        """

        # store reference to datafields
        self.dfRef = dfRef
        self.dfEval = dfEval

        # the methods to use to get coordinates and indices from dfEval. These
        # depend on whether the evaluation datafield is in 'center' or 'node'
        # mode
        self._getEvalCoordsMesh = None
        self._getEvalCoords = None
        self._getEvalIdx = None

        # the methods to use to get coordinates from dfRef. These depends
        # on whether the reference datafield is in 'center' or 'node' mode
        self._getRefCoords = None

        #check that the datafields are comparable and define the appropriate
        # methods for coordinate and index retrieval based on the datafield
        # modes
        self._checkAndPrepare()

    def _checkAndPrepare(self):
        r"""

        """

        # get the boundary coordinates of the reference array...
        coordsRefP0 = self.dfRef.dataGrid.getCoordsEdge([0, 0])
        coordsRefP1 = self.dfRef.dataGrid.getCoordsEdge(
            [self.dfRef.dataGrid.NOE_X - 1,
             self.dfRef.dataGrid.NOE_Y - 1])

        # ...and ensure its within the bounds of the evaluation array
        if not (self.dfEval.dataGrid.isCoordsInEdgeBounds(coordsRefP0) and
                    self.dfEval.dataGrid.isCoordsInEdgeBounds(coordsRefP1)):
            raise ValueError(
                "The reference datafield 'dfRef' is not entirely within the "
                "bounds of the evaluation datafield 'dfEval'. Gamma analysis "
                "can not be performed")


        # define which methods are used to get coordinates from the dfEval.
        # This depends on the datafield's mode
        if self.dfEval.mode == "center":
            self._getEvalCoordsMesh = self.dfEval.dataGrid.createMeshCenters
            self._getEvalCoords = self.dfEval.dataGrid.getCoordsCenter
            self._getEvalIdx = self.dfEval.dataGrid.findCoordsCenterIdx
        else:
            self._getEvalCoordsMesh = self.dfEval.dataGrid.createMeshEdges
            self._getEvalCoords = self.dfEval.dataGrid.getCoordsEdge
            self._getEvalIdx = self.dfEval.dataGrid.findCoordsEdgeIdx

        # define which methods are used to get coordinates from the dfRef.
        # This depends on the datafield's mode
        if self.dfEval.mode == "center":
            self._getRefCoords = self.dfRef.dataGrid.getCoordsCenter
        else:
            self._getRefCoords = self.dfRef.dataGrid.getCoordsEdge

    def calculateGamma(self, DTA, DD, isDDglobal=False):
        r"""

        """

        # create a coordinate mesh for the evaluation datafield
        meshCoordsEval = self._getEvalCoordsMesh()

        # create empty array with same size as the reference array
        arrGamma = numpy.zeros(self.dfRef.dataArray.shape)

        # get the global maximum in the reference (optional)
        valRefMax = self.dfRef.dataArray.max() if isDDglobal else None

        # loop through the reference points and calculate each squared gamma
        # index
        for i in range(arrGamma.shape[0]):
            for j in range(arrGamma.shape[1]):
                # get the reference point's value indices, value,
                # and coordinate
                idxRefP = idx2D([i, j])  # index
                valRefP = self.dfRef.dataArray[idxRefP.i,
                                               idxRefP.j]  #coordinates
                coordsRefP = self._getRefCoords(idxRefP)  # value

                # define dose criterion (local or global)
                cDD = DD * valRefMax if isDDglobal else DD

                #calculate the squared gamma index for the given point
                arrGamma[i, j] = self._calcGammaIdxSq(coordsRefP,
                                                      valRefP,
                                                      DTA,
                                                      cDD,
                                                      meshCoordsEval)

        # get the sqrt of arrGamma to get the actual indices
        arrGamma = numpy.sqrt(arrGamma)

        # create a new datafield containing the gamma indices
        dfGamma = datafield2D(self.dfRef.dataGrid,
                              arrGamma,
                              self.dfRef.mode,
                              deepCopy=True)

        return dfGamma

    def _calcGammaIdxSq(self,
                        coordsRefP,
                        valRefP,
                        DTA,
                        cDD,
                        meshCoordsEval):
        r"""

        """

        # get indices of closest evaluation point
        idxEvalP = self._getEvalIdx(coordsRefP)
        # get coordinates of that evaluation point
        coordsEvalP = self._getEvalCoords(idxEvalP)

        # calculate the search-cube indices
        idxCubeP0 = self._getEvalIdx(coordsEvalP - DTA)
        idxCubeP1 = self._getEvalIdx(coordsEvalP + DTA)
        # create 'slice' objects for the search-cube bounds
        sliceCubeI = slice(idxCubeP0.i, idxCubeP1.i + 1)
        sliceCubeJ = slice(idxCubeP0.j, idxCubeP1.j + 1)

        # calculate the squared distance between the reference point and each
        # evaluation point in the search-cube
        arrCubeDistSq = ((meshCoordsEval[0][sliceCubeI,
                                            sliceCubeJ] -
                          coordsRefP.x) ** 2 +
                         (meshCoordsEval[1][sliceCubeI,
                                            sliceCubeJ] -
                          coordsRefP.y) ** 2)

        # create a boolean mask of the search-sphere (its not supposed to be a
        # cube normally, its just a convenience)
        _mask = arrCubeDistSq <= DTA**2

        # retrieve the evaluation datafield values within the search-cube
        arrCubeVal = self.dfEval.dataArray[sliceCubeI,
                                           sliceCubeJ]

        # calculate the squared gamma indices within the search-cube
        arrCubeGammaSq = ((arrCubeVal - valRefP) ** 2 / cDD ** 2 +
                          arrCubeDistSq / DTA ** 2)

        # the gamma index is considered to be the best index, i.e., the minimum
        # one, out of all indices calculated within the search-cube after its
        # masked (with the search-sphere mask)
        gammaIdxSq = arrCubeGammaSq[_mask].min()

        return gammaIdxSq

class gammaCalculator3D(object):
    r"""

    """

    def __init__(self, dfRef, dfEval):
        r"""

        """

        # store reference to datafields
        self.dfRef = dfRef
        self.dfEval = dfEval

        # the methods to use to get coordinates and indices from dfEval. These
        # depend on whether the evaluation datafield is in 'center' or 'node'
        # mode
        self._getEvalCoordsMesh = None
        self._getEvalCoords = None
        self._getEvalIdx = None

        # the methods to use to get coordinates from dfRef. These depends
        # on whether the reference datafield is in 'center' or 'node' mode
        self._getRefCoords = None

        #check that the datafields are comparable and define the appropriate
        # methods for coordinate and index retrieval based on the datafield
        # modes
        self._checkAndPrepare()

    def _checkAndPrepare(self):
        r"""

        """

        # get the boundary coordinates of the reference array...
        coordsRefP0 = self.dfRef.dataGrid.getCoordsEdge([0, 0, 0])
        coordsRefP1 = self.dfRef.dataGrid.getCoordsEdge(
            [self.dfRef.dataGrid.NOE_X - 1,
             self.dfRef.dataGrid.NOE_Y - 1,
             self.dfRef.dataGrid.NOE_Z - 1])

        # ...and ensure its within the bounds of the evaluation array
        if not (self.dfEval.dataGrid.isCoordsInEdgeBounds(coordsRefP0) and
                    self.dfEval.dataGrid.isCoordsInEdgeBounds(coordsRefP1)):
            raise ValueError(
                "The reference datafield 'dfRef' is not entirely within the "
                "bounds of the evaluation datafield 'dfEval'. Gamma analysis "
                "can not be performed")


        # define which methods are used to get coordinates from the dfEval.
        # This depends on the datafield's mode
        if self.dfEval.mode == "center":
            self._getEvalCoordsMesh = self.dfEval.dataGrid.createMeshCenters
            self._getEvalCoords = self.dfEval.dataGrid.getCoordsCenter
            self._getEvalIdx = self.dfEval.dataGrid.findCoordsCenterIdx
        else:
            self._getEvalCoordsMesh = self.dfEval.dataGrid.createMeshEdges
            self._getEvalCoords = self.dfEval.dataGrid.getCoordsEdge
            self._getEvalIdx = self.dfEval.dataGrid.findCoordsEdgeIdx

        # define which methods are used to get coordinates from the dfRef.
        # This depends on the datafield's mode
        if self.dfEval.mode == "center":
            self._getRefCoords = self.dfRef.dataGrid.getCoordsCenter
        else:
            self._getRefCoords = self.dfRef.dataGrid.getCoordsEdge

    def calculateGamma(self, DTA, DD, isDDglobal=False):
        r"""

        """

        # create a coordinate mesh for the evaluation datafield
        meshCoordsEval = self._getEvalCoordsMesh()

        # create empty array with same size as the reference array
        arrGamma = numpy.zeros(self.dfRef.dataArray.shape)

        # get the global maximum in the reference (optional)
        valRefMax = self.dfRef.dataArray.max() if isDDglobal else None

        # loop through the reference points and calculate each squared gamma
        # index
        for i in range(arrGamma.shape[0]):
            for j in range(arrGamma.shape[1]):
                for k in range(arrGamma.shape[2]):
                    # get the reference point's value indices, value,
                    # and coordinate
                    idxRefP = idx3D([i, j, k])  # index
                    valRefP = self.dfRef.dataArray[idxRefP.i,
                                                   idxRefP.j,
                                                   idxRefP.k]  #coordinates
                    coordsRefP = self._getRefCoords(idxRefP)  # value

                    # define dose criterion (local or global)
                    cDD = DD * valRefMax if isDDglobal else DD

                    #calculate the squared gamma index for the given point
                    arrGamma[i, j, k] = self._calcGammaIdxSq(coordsRefP,
                                                             valRefP,
                                                             DTA,
                                                             cDD,
                                                             meshCoordsEval)

        # get the sqrt of arrGamma to get the actual indices
        arrGamma = numpy.sqrt(arrGamma)

        # create a new datafield containing the gamma indices
        dfGamma = datafield3D(self.dfRef.dataGrid,
                              arrGamma,
                              self.dfRef.mode,
                              deepCopy=True)

        return dfGamma

    def _calcGammaIdxSq(self,
                        coordsRefP,
                        valRefP,
                        DTA,
                        cDD,
                        meshCoordsEval):
        r"""

        """

        # get indices of closest evaluation point
        idxEvalP = self._getEvalIdx(coordsRefP)
        # get coordinates of that evaluation point
        coordsEvalP = self._getEvalCoords(idxEvalP)

        # calculate the search-cube indices
        idxCubeP0 = self._getEvalIdx(coordsEvalP - DTA)
        idxCubeP1 = self._getEvalIdx(coordsEvalP + DTA)
        # create 'slice' objects for the search-cube bounds
        sliceCubeI = slice(idxCubeP0.i, idxCubeP1.i + 1)
        sliceCubeJ = slice(idxCubeP0.j, idxCubeP1.j + 1)
        sliceCubeK = slice(idxCubeP0.k, idxCubeP1.k + 1)

        # calculate the squared distance between the reference point and each
        # evaluation point in the search-cube
        arrCubeDistSq = ((meshCoordsEval[0][sliceCubeI,
                                            sliceCubeJ,
                                            sliceCubeK] -
                          coordsRefP.x) ** 2 +
                         (meshCoordsEval[1][sliceCubeI,
                                            sliceCubeJ,
                                            sliceCubeK] -
                          coordsRefP.y) ** 2 +
                         (meshCoordsEval[2][sliceCubeI,
                                            sliceCubeJ,
                                            sliceCubeK] -
                          coordsRefP.z) ** 2)

        # create a boolean mask of the search-sphere (its not supposed to be a
        # cube normally, its just a convenience)
        _mask = arrCubeDistSq <= DTA**2

        # retrieve the evaluation datafield values within the search-cube
        arrCubeVal = self.dfEval.dataArray[sliceCubeI,
                                           sliceCubeJ,
                                           sliceCubeK]

        # calculate the squared gamma indices within the search-cube
        arrCubeGammaSq = ((arrCubeVal - valRefP) ** 2 / cDD ** 2 +
                          arrCubeDistSq / DTA ** 2)

        # the gamma index is considered to be the best index, i.e., the minimum
        # one, out of all indices calculated within the search-cube after its
        # masked (with the search-sphere mask)
        gammaIdxSq = arrCubeGammaSq[_mask].min()

        return gammaIdxSq