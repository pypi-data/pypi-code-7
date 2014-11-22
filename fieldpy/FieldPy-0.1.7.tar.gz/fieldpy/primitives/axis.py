"""
This module contains axis primitive classes
"""

from __future__ import division
import numpy


class axis(object):
    r"""One-dimensional rectilinear axis class

    This class is meant to serve as a container of a rectilinear axis and
    provide functionality such as shifting, subsetting, and methods to
    find the index of a particular coordinate etc.

    Attributes:


    """

    def __init__(self, coordsEdges, deepCopy=True):
        r"""Class construction and initialization

        This method constructs and initializes the 'axis' object given a
        numpy.ndarray, a list, or tuple containing the cell edge coordinates
        defining this axis. All these quantities are stored within this object
        as 'numpy.ndarray' objects

        Note:
            The coordinates must be monotonically increasing. Otherwise an
            error will be raised

        Parameters:
            coordsEdges (numpy.ndarray, list, or tuple): The coordinates of
                the cell edges that define the axis
            deepCopy (bool, optional): Whether the coordinates will be
                deep-copied or not. It only applies to coordinates provided in
                a 'numpy.ndarray', happens by default if a list or tuple is
                provided. Strongly recommended cause if the edge coordinates are
                changed outside the class then the product quantities will be
                wrong. Defaults to "True"

        Returns:
            A new 'axis' object with all the relevant quantities already
            calculated
        """

        #check the type of the given 'coordsEdges' object
        if (type(coordsEdges) == list) or (type(coordsEdges) == tuple):
            self.coordsEdges = numpy.array(coordsEdges)
        elif (type(coordsEdges) == numpy.ndarray):
            self.coordsEdges = coordsEdges.copy() if deepCopy else coordsEdges
        else:
            raise TypeError(
                "The given 'coordsEdges' object should be a 'numpy.ndarray', "
                "a 'list' or a 'tuple'. Returning 'None'")

        #check the coordinates (for shape)
        if self.coordsEdges.ndim != 1: #if the object is not 1D then...
            raise ValueError(
                "The given 'coordsEdges' object should be one-dimensional. "
                "Returning 'None'")

        #check the coordinates (for size)
        if len(
                self.coordsEdges) < 2: #if less than three coordinates were
                # given then this is not an axis (but a single cell)
            raise ValueError(
                "The given 'coordsEdges' object must contain at least 2 "
                "coordinates. Returning 'None'")

        if not self._isMonotonicallyIncreasing(self.coordsEdges):
            raise ValueError(
                "The given 'coordsEdges' must be monotonically increasing")

        #the number of cells on the axis
        self.noCells = len(self.coordsEdges) - 1
        #the number of edges on the axis
        self.noEdges = len(self.coordsEdges)

        #calculate secondary quantities
        self._update()

    def _isMonotonicallyIncreasing(self, coordsEdges):
        r"""Checks whether the coordinates are monotonically increasing"""

        diffs = coordsEdges[1:]-coordsEdges[0:-1]
        if not (diffs>0).all():
            return False

        return True

    def _update(self):
        r"""Calculates secondary quantities of the axis

        This method (re-)calculates the secondary quantities of the axis based
        on the initial 'coordsEdges' values. These quantities include the
        'coordsCenters' and 'widths'. This method should not be called directly
        """

        #(re-)calculate the cell widths
        self._calcWidths()

        #(re-)calculate the cell center coordinates
        self._calcCoordsCenters()

    def _calcWidths(self):
        r"""Calculates the cell widths

        This method calculates the cell widths, i.e., distances between the
        cell edges, along the axis
        """

        #create a new appropriately sized array where the widths are stored
        self.widths = numpy.zeros((self.noCells))

        #calculate the widths
        self.widths = abs(self.coordsEdges[1:] - self.coordsEdges[0:-1])

    def _calcCoordsCenters(self):
        r"""Calculates the cell center coordinates

        This method calculates the coordinates of the cell centers along the
        axis
        """

        #create a new appropriately sized array where the coordinates are stored
        self.coordsCenters = numpy.zeros((self.noCells))

        #calculate the coordinates
        self.coordsCenters = self.coordsEdges[0:-1] + 0.5 * self.widths

    def __len__(self):
        r"""Overloader of the 'len' builtin"""

        return self.noEdges

    def isCoordInEdgeBounds(self, coordinate):
        r"""Checks if 'coordinate' is within the 'edge' bounds

        This method checks if 'coordinate' is within the bounds defined by the
        axis cell edges as defined in 'coordsEdges'. The check is done by
        through the 'min' and 'max' of 'coordsEdges'

        Parameters:
            coordinate (float):  The coordinate for which the check is performed

        Returns:
            "True" if the 'coordinate' is within the bounds and "False" if not
        """

        if self.coordsEdges.min() <= coordinate <= self.coordsEdges.max():
            return True

        return False

    def isCoordInCenterBounds(self, coordinate):
        r"""Checks if 'coordinate' is within the 'center' bounds

        This method checks if 'coordinate' is within the bounds defined by the
        axis cell center as defined in 'coordsCenters'. The check is done by
        through the 'min' and 'max' of 'coordsCenters'

        Parameters:
            coordinate (float):  The coordinate for which the check is performed

        Returns:
            "True" if the 'coordinate' is within the bounds and "False" if not
        """

        if self.coordsCenters.min() <= coordinate <= self.coordsCenters.max():
            return True

        return False

    def findCoordEdgeIdx(self, coordinate):
        r"""Find the nearest cell edge index for a given 'coordinate'

        This method first checks whether the given 'coordinate' is within the
        bounds of the axis and if so it finds and returns the index of the
        closest existing cell edge coordinate on the axis. If the 'coordinate'
        is outside the bounds then either the first or last index is returned
        (depending on the 'coordinate')

        Parameters:
            coordinate (float): The value of the cell edge coordinate the
                cell edge index is wanted for

        Returns:
            An integer containing the found index
        """

        if self.isCoordInEdgeBounds(coordinate): #coordinate within bounds
            return (numpy.abs(self.coordsEdges - coordinate)).argmin()
        elif coordinate < self.coordsEdges.min(): #coordinate before axis
            return 0
        elif coordinate > self.coordsEdges.max(): #coordinate after axis
            return self.noEdges - 1

    def findCoordCenterIdx(self, coordinate):
        r"""Find the nearest cell center index for a given 'coordinate'

        This method first checks whether the given 'coordinate' is within the
        bounds of the axis and if so it finds and returns the index of the
        closest existing cell center coordinate on the axis. If the 'coordinate'
        is outside the bounds then either the first or last index is returned
        (depending on the 'coordinate')

        Parameters:
            coordinate (float): The value of the cell center coordinate the
                cell edge index is wanted for

        Returns:
            An integer containing the found index
        """

        if self.isCoordInCenterBounds(coordinate): #coordinate within bounds
            return (numpy.abs(self.coordsCenters - coordinate)).argmin()
        elif coordinate < self.coordsCenters.min(): #coordinate before axis
            return 0
        elif coordinate > self.coordsCenters.max(): #coordinate after axis
            return self.noCells - 1

    def shiftAxis(self, coordShift):
        r"""Shifts the 'axis' data by 'coordShift'

        This method adds a 'coordShift' to the 'coordsEdges' and re-calculates
        all the secondary quantities

        Parameters:
            coordShift (int or float): The shift added to 'coordsEdges' (can be
            either positive or negative)
        """

        #add 'shift' to 'coordsCellEdges'
        self.coordsEdges += coordShift
        #re-calculate all secondary quantities
        self._update()

    def findMinWidth(self):
        r"""Returns the minimum cell width"""

        #calculate and return the minimum cell width
        return self.widths.min()

    def findMaxWidth(self):
        r"""Returns the maximum cell width"""

        #calculate and return the maximum cell width
        return self.widths.max()

    def createSubset(self, coordStart, coordStop):
        r"""Returns a new 'axis' which is a subset of the original one

        This method creates and returns a new 'axis' object that is a subset of
        the original object. It uses the 'findCoordEdgeIdx' method to find the
        indices of 'coordStart' and 'coordStop', slices the 'coordsEdges'
        array, and returns a new object based on this sliced array. If either
        of the defined coordinates are outside the original bounds then the new
        'axis' will either start at the beginning of the original and/or stop
        at its end.

        Parameters:
            coordStart (float): The cell edge coordinate at which the new 'axis'
                will start
            coordStop (float): The cell edge coordinate at which the new 'axis'
                will stop

        Returns:
            A new 'axis' object where the 'coordsEdges' values are an
            appropriate subset of the original one
        """

        #find the indices of corresponding to the 'coordStart' coordinate
        idxStart = self.findCoordEdgeIdx(coordStart)
        #find the indices of corresponding to the 'coordStop' coordinate
        idxStop = self.findCoordEdgeIdx(coordStop)

        if ((idxStart == 0 and idxStop == 0) or
                (idxStart == self.noEdges - 1 and idxStop == self.noEdges - 1)):
            raise ValueError("Inappropriate coordinates gives")

        #if the 'coordStop' coordinate yields the last viable index of the
        #original array then...
        if idxStop == (self.noEdges - 1):
            #...use 'coordStart' only and return a new 'axis'
            return axis(self.coordsEdges[idxStart:])

        #create and return a new 'axis' object using the subset of the original
        #'coordsEdges' array. Note that we add "1" to 'idxStop' so that that
        #index will also be included
        return axis(self.coordsEdges[idxStart:idxStop + 1])

    def createExtended(self, direction, noCells, widthCells = None):
        r"""Returns a new extended axis

        This method creates and returns a new 'axis' object which has been
        extended towards a given direction ("left", "rigth", or "both") by a
        number of cells (either the same for both directions or different) and
        cell-width which can either be replicated from the nearest cell (to the
        direction of the extension) or specified (either the same for both
        directions or different).

        Parameters:
            direction (str): The direction of extension. Should be "left",
                "right", or "both".
            noCells (int, list, or tuple): The number of cells to extend the
                axis by. Should either be a single integer or a list/tuple with
                the number of cells extension happens with in the left/right
                direction.
            widthCells (float, list, or tuple, optional): The cell-width by
                which the axis is extended. Defaults to the nearest cell-width
                of the axis. Alternatively it should either be a single float
                or a list/tuple with the cell-widths extension happens with in
                the left/right direction.

        Returns:
            axisNew (axis.axis): The new extended 'axis' object
        """

        #check the 'direction' parameter
        if not direction in ["left", "right", "both"]:
            raise ValueError(
                "Invalid 'direction' provided. It should be 'left', 'right', "
                "or 'both'")

        #check the 'noCells' parameters
        if not (isinstance(noCells, int) or
                isinstance(noCells, list) or
                isinstance(noCells, tuple)):
            raise ValueError(
                "Invalid 'noCells' provided. It should be an non-zero "
                "integer number or a list/tuple of two such values")

        #check the 'widthCells' parameters
        if widthCells is not None:
            if not (isinstance(widthCells, float) or
                    isinstance(widthCells, list) or
                    isinstance(widthCells, tuple)):
                raise ValueError(
                    "Invalid 'widthCells' provided. It should be a positive "
                    "float number or a list/tuple of two such values")

        #get appropriate 'noCells'
        if isinstance(noCells, int): #single integer
            noCellsL = noCells
            noCellsR = noCells
        else: #list/tuple of integers
            if not len(noCells) >= 2:
                raise ValueError(
                    "Invalid 'noCells' provided. It should be an non-zero "
                    "integer number or a list/tuple of two such values")
            noCellsL = noCells[0]
            noCellsR = noCells[1]

        #get appropriate 'widthCells'
        if widthCells is None:
            widthCellsL = self.widths[0]
            widthCellsR = self.widths[-1]
        else:
            if isinstance(widthCells, float): #single float
                widthCellsL = widthCells
                widthCellsR = widthCells
            else: #list/tuple of floats
                if not len(widthCells) >= 2:
                    raise ValueError(
                        "Invalid 'widthCells' provided. It should be an "
                        "non-zero integer number or a list/tuple of two such "
                        "values")
                widthCellsL = widthCells[0]
                widthCellsR = widthCells[1]

        #create a copy of the edge coordinates array
        coordsEdgesNew = self.coordsEdges.copy()

        #insert left edges (optionally)
        if direction in ["left", "both"]:
            #calculate and insert new left edges at the beginning
            for i in range(1, noCellsL+1):
                coordsEdgesNew = numpy.insert(coordsEdgesNew,
                                              0,
                                              (self.coordsEdges[0] -
                                               i*widthCellsL))

        #insert right edges (optionally)
        if direction in ["right", "both"]:
            #calculate and insert new right edges at the end
            for i in range(1, noCellsR+1):
                coordsEdgesNew = numpy.append(coordsEdgesNew,
                                              (self.coordsEdges[-1] +
                                               i*widthCellsR))

        #create new extended axis
        axisExtended = axis(coordsEdgesNew)

        return axisExtended