"""
This module contains grid primitive classes
"""

from __future__ import division
import numpy

from fieldpy.primitives import point
from fieldpy.primitives import axis
from fieldpy.primitives import idx


def ndmesh(*args):
    """

    """
    args = map(numpy.asarray, args)
    return numpy.broadcast_arrays(
        *[x[(slice(None),) + (None,) * i] for i, x in enumerate(args)])


class grid2D(object):
    r"""Two-dimensional rectilinear grid class

    This class acts as a wrapper of two 'axis' objects to define a 2D
    rectilinear grid

    Attributes:
        axis_x (axis): An 'axis' object storing the x axis coordinates
        axis_y (axis): An 'axis' object storing the y axis coordinates
        NOE_X (int): The number of edges (NOE) along the x axis
        NOE_Y (int): The number of edges (NOE) along the y axis
        NOC_X (int): The number of cells (NOC) along the x axis
        NOC_Y (int): The number of cells (NOC) along the y axis

    """

    def __init__(self, axis_x, axis_y, deepCopy=True):
        r"""Class construction and initialization

        This method constructs and initializes the 'grid' object given two
        'axis.axis' objects that define it.

        Parameters:
            axis_x (axis.axis): The x axis of the grid
            axis_y (axis.axis): The y axis of the grid
            deepCopy (bool, optional): Whether the provided axes will be
                deep-copied or not. Strongly recommended cause if the axes
                are changed outside the class then the product quantities
                will be wrong. Defaults to "True"

        Returns:
            A new 'grid2D' object with the two given axes
        """

        #store/recreate the 'axis' objects
        self.axis_x = axis.axis(axis_x.coordsEdges) if deepCopy else axis_x
        self.axis_y = axis.axis(axis_y.coordsEdges) if deepCopy else axis_y

        #store numbers of edges (NOE)
        self.NOE_X = self.axis_x.noEdges
        self.NOE_Y = self.axis_y.noEdges

        #store number of cells (NOC)
        self.NOC_X = self.axis_x.noCells
        self.NOC_Y = self.axis_y.noCells

    def createSubset(self, coordsStart, coordsStop):
        r"""Returns a new 'grid2D' which is a subset of the original one

        This method creates and returns a new 'grid2D' object that is a subset
        of the original object. It uses the 'createSubset' method of its 'axis'
        objects to create new sub-axes and then returns a new 'grid2D'
        initialized with those axes. The 'coordsStart' and 'coordsStop'
        parameters contain the coordinates at which the subset is created with
        'coordStart' containing the x and y coordinates the subset starts from
        and 'coordsStop', the coordinates where it ends. These needn't be exact
        coordinates, the nearest ones will be found. These parameters may either
        be 'pointCart2D' objects, lists, or tuples.

        Parameters:
            coordsStart (pointCart2D, list, or tuple): The x and y coordinates
                where the subset will start from
            coordsStop (pointCart2D, list, or tuple): The x and y coordinates
                where the subset will stop at

        Returns:
            A new 'grid' object where the x and y axes are subsets of the
            original object
        """

        #convert the given coordinates
        coordsStart = point.pointCart2D(coordsStart)
        coordsStop = point.pointCart2D(coordsStop)

        #call the 'createSubset' method of each axis and create a new sub-axis
        sub_axis_x = self.axis_x.createSubset(coordsStart.x, coordsStop.x)
        sub_axis_y = self.axis_y.createSubset(coordsStart.y, coordsStop.y)

        #create and return a new 'grid2D' object that is a subset of the
        #original
        return grid2D(sub_axis_x, sub_axis_y)

    def shiftGrid(self, coordsShift):
        r"""Shifts the object's 'axis' data by 'coordsShift'

        This method uses the 'shiftAxis' method of its 'axis' objects to shift
        them by 'coordsShift' which is either a 'pointCart2D', a list, a tuple,
        or a numpy.ndarray object containing the x and y coordinates shifts
        the 'grid2D' is shifted by

        Parameters:
            coordsShift (pointCart2D, list, tuple, or numpy.ndarray): The
                coordinates the grid is shifted by
        """

        #convert the given coordinates
        coordsShift = point.pointCart2D(coordsShift)

        self.axis_x.shiftAxis(coordsShift.x)
        self.axis_y.shiftAxis(coordsShift.y)

    def isCoordsInEdgeBounds(self, coords):
        r"""Checks if 'coords' is within the 'edge' bounds

        This method uses the 'isCoordInEdgeBounds' method of its 'axis' objects
        to check whether 'coords' is within the grid's 'edge' bounds. The
        'coords' parameter may be a 'pointCart2D', a list, a tuple, or a
        numpy.ndarray object containing the x and y coordinates to be
        evaluated

        Parameters:
            coords (pointCart2D, list, tuple, or numpy.ndarray): The
                coordinates to be evaluated

        Returns:
            "True" if 'coords' are within the bounds and "False" if not
        """

        #convert the given coordinates
        coords = point.pointCart2D(coords)

        if (self.axis_x.isCoordInEdgeBounds(coords.x) and
                self.axis_y.isCoordInEdgeBounds(coords.y)):
            return True

        return False

    def isCoordsInCenterBounds(self, coords):
        r"""Checks if 'coords' is within the 'center' bounds

        This method uses the 'isCoordInEdgeBounds' method of its 'axis' objects
        to check whether 'coords' is within the grid's 'center' bounds. The
        'coords' parameter may be a 'pointCart2D', a list, a tuple, or a
        numpy.ndarray object containing the x and y coordinates to be
        evaluated

        Parameters:
            coords (pointCart2D, list, tuple, or numpy.ndarray): The
                coordinates to be evaluated

        Returns:
            "True" if 'coords' are within the bounds and "False" if not
        """

        #convert the given coordinates
        coords = point.pointCart2D(coords)

        if (self.axis_x.isCoordInCenterBounds(coords.x) and
                self.axis_y.isCoordInCenterBounds(coords.y)):
            return True

        return False

    def findCoordsEdgeIdx(self, coords):
        r"""Finds the nearest cell edge indices for given 'coords'

        This method uses the 'findCoordEdgeIdx' method of its 'axis' objects to
        find and return the indices of the nearest existing cell edge
        coordinates on the grid

        Parameters:
            coords (pointCart2D, list, tuple, or numpy.ndarray): The
                coordinates for which the edge indices are found

        Returns:
            A 'idx.idx2D' object containing the found indices
        """

        #convert the given coordinates
        coords = point.pointCart2D(coords)

        i = self.axis_x.findCoordEdgeIdx(coords.x)
        j = self.axis_y.findCoordEdgeIdx(coords.y)

        return idx.idx2D([i, j])

    def findCoordsCenterIdx(self, coords):
        r"""Finds the nearest cell center indices for given 'coords'

        This method uses the 'findCoordEdgeIdx' method of its 'axis' objects to
        find and return the indices of the nearest existing cell center
        coordinates on the grid

        Parameters:
            coords (pointCart2D, list, tuple, or numpy.ndarray): The
                coordinates for which the center indices are found

        Returns:
            A 'idx.idx2D' object containing the found indices
        """

        #convert the given coordinates
        coords = point.pointCart2D(coords)

        i = self.axis_x.findCoordCenterIdx(coords.x)
        j = self.axis_y.findCoordCenterIdx(coords.y)

        return idx.idx2D([i, j])

    def getCoordsEdge(self, indices):
        r"""Returns the edge coordinates for given 'indices'

        This method uses the 'indices' and directly accesses the
        'coordsEdges' of the grid's 'axis' objects and returns the actual
        coordinates as a 'pointCart2D' object

        Parameters:
            indices (idx2D, list, tuple, or numpy.ndarray): The
                indices for which the edge coordinates are returned

        Returns:
            A 'point.pointCart2D' object with the found coordinates
        """

        #convert the given indices
        indices = idx.idx2D(indices)

        #get the 'x' and 'y' coordinates for the given indices
        x = self.axis_x.coordsEdges[indices.i]
        y = self.axis_y.coordsEdges[indices.j]

        return point.pointCart2D([x, y])

    def getCoordsCenter(self, indices):
        r"""Returns the center coordinates for given 'indices'

        This method uses the 'indices' and directly accesses the
        'coordsCenters' of the grid's 'axis' objects and returns the actual
        coordinates as a 'pointCart2D' object

        Parameters:
            indices (idx2D, list, tuple, or numpy.ndarray): The
                indices for which the edge coordinates are returned

        Returns:
            A 'point.pointCart2D' object with the found coordinates
        """

        #convert the given indices
        indices = idx.idx2D(indices)

        #get the 'x' and 'y' coordinates for the given indices
        x = self.axis_x.coordsCenters[indices.i]
        y = self.axis_y.coordsCenters[indices.j]

        return point.pointCart2D([x, y])

    def getCoordsBounds(self):
        r"""Returns the coordinates of the grid's boundaries

        This method returns two sets of coordinates representing the corners
        of the grid. These coordinates are the first and last edges of the grid
        along the respective axes.

        Returns:
            coordsStart (pointCart2D): The xStart and yStart edge coordinates
            coordsStop (pointCart2D): The xStop and yStop edge coordinates
        """

        coordsStart = point.pointCart2D([self.axis_x.coordsEdges[0],
                                        self.axis_y.coordsEdges[0]])
        coordsStop = point.pointCart2D([self.axis_x.coordsEdges[-1],
                                        self.axis_y.coordsEdges[-1]])

        return coordsStart, coordsStop

    def createMeshEdges(self):
        r"""Creates and returns an edge coordinate mesh"""

        #create and return the edge coordinate mesh
        mesh = ndmesh(self.axis_x.coordsEdges,
                      self.axis_y.coordsEdges)

        #transpose each mesh (to abide by the x-y-z order)
        mesh[0] = mesh[0].transpose()
        mesh[1] = mesh[1].transpose()

        return mesh

    def createMeshCenters(self):
        r"""Creates and returns an center coordinate mesh"""

        #create and return the center coordinate mesh
        mesh = ndmesh(self.axis_x.coordsCenters,
                      self.axis_y.coordsCenters)

        #transpose each mesh (to abide by the x-y-z order)
        mesh[0] = mesh[0].transpose()
        mesh[1] = mesh[1].transpose()

        return mesh

    def calcCellAreas(self):
        r"""Creates and returns an array with the area of each cell"""

        meshWidths = ndmesh(self.axis_x.widths, self.axis_y.widths)

        return (meshWidths[0] * meshWidths[1]).transpose()

    def createCenterGrid(self):
        r"""Returns a new 'grid2D' where the former centers are now the edges

        This method creates and returns a new 'grid2D' object where the current
        cell-center coordinates are the edges in this new grid. Essentially this
        method removes half a layer of cells from around the grid.

        Returns:
            gridNew (grid.grid2D): The new cell-centers grid
        """

        axis_x_new = axis.axis(self.axis_x.coordsCenters)
        axis_y_new = axis.axis(self.axis_y.coordsCenters)

        gridNew = grid2D(axis_x_new,
                         axis_y_new)

        return gridNew

    def createExtended(self, noCellsX, noCellsY):
        r"""Returns a new extended grid

        This method creates and returns a new 'grid2D' object which has been
        extended in all directions by a number of cells (either the same for
        both directions or different) and the cell-width which is replicated
        from the nearest cell (to the direction of the extension).

        Note:
            This method is a simple wrapper around the 'createExtended' method
            in the axis.axis class. That function offers much more extension
            possiblities and complicated should be done by manually extending
            each axis through that method and then manually creating a new grid.

        Parameters:
            noCellsX (int, list, or tuple): The number of cells to extend the
                axis X by. Should either be a single integer or a list/tuple
                with the number of cells extension happens with in the
                left/right direction.
            noCellsY (int, list, or tuple): The number of cells to extend the
                axis Y by. Should either be a single integer or a list/tuple
                with the number of cells extension happens with in the
                left/right direction.

        Returns:
            gridNew (grid.grid2D): The new extended 'grid2D' object
        """

        axis_x_new = self.axis_x.createExtended("both", noCellsX)
        axis_y_new = self.axis_y.createExtended("both", noCellsY)

        gridNew = grid2D(axis_x_new,
                         axis_y_new)

        return gridNew

    def isCartesian(self, error=1.0e-6):
        r"""Checks whether the grid is cartesian

        This method checks whether the current grid is cartesian, i.e., whether
        the cells widths are equal and whether all cells have the same widths
        (i.e., whether the grid is regular).

        Parameters:
            error (float, optional): The maximum allowed difference between
                cell widths in order for them to be considered equal. Defaults
                to "1.0e-6"

        Returns:
            isUni (bool): "True" if the grid is cartesian and "False" otherwise
        """

        #get the widths of the first cell on each axis
        w0x = self.axis_x.widths[0]
        w0y = self.axis_y.widths[0]

        #check the first widths of the different axes
        if abs(w0x - w0y) > error:
            return False

        return self.isRegular()

    def isRegular(self, error=1.0e-6):
        r"""Checks whether the grid is regular

        This method checks whether the current grid is regular, i.e., whether
        the cell widths along each axis (but between axes) are equal.

        Parameters:
            error (float, optional): The maximum allowed difference between
                cell widths in order for them to be considered equal. Defaults
                to "1.0e-6"

        Returns:
            isUni (bool): "True" if the grid is regular and "False" otherwise
        """

        #get the widths of the first cell on each axis
        w0x = self.axis_x.widths[0]
        w0y = self.axis_y.widths[0]

        #check for regularity along each axis
        if not ((numpy.abs(self.axis_x.widths - w0x).max() <= error) and
                (numpy.abs(self.axis_y.widths - w0y).max() <= error)):
            return False

        return True


class grid3D(object):
    r"""Three-dimensional rectilinear grid class

    This class acts as a wrapper of two 'axis' objects to define a 3D
    rectilinear grid

    Attributes:
        axis_x (axis): An 'axis' object storing the x axis coordinates
        axis_y (axis): An 'axis' object storing the y axis coordinates
        axis_z (axis): An 'axis' object storing the z axis coordinates
        NOE_X (int): The number of edges (NOE) along the x axis
        NOE_Y (int): The number of edges (NOE) along the y axis
        NOE_Z (int): The number of edges (NOE) along the z axis
        NOC_X (int): The number of cells (NOC) along the x axis
        NOC_Y (int): The number of cells (NOC) along the y axis
        NOC_Z (int): The number of cells (NOC) along the z axis
    """

    def __init__(self, axis_x, axis_y, axis_z, deepCopy=True):
        r"""Class construction and initialization

        This method constructs and initializes the 'grid3D' object given three
        'axis.axis' objects that define it.

        Note:
            A deepcopy of the 'axis' objects is performed to avoid breaking the
                links

        Parameters:
            axis_x (axis.axis): The x axis of the grid
            axis_y (axis.axis): The y axis of the grid
            axis_y (axis.axis): The y axis of the grid
            deepCopy (bool, optional): Whether the provided axes will be
                deep-copied or not. Strongly recommended cause if the axes
                are changed outside the class then the product quantities
                will be wrong. Defaults to "True"

        Returns:
            A new 'grid3D' object with the three given axes
        """

        #store/recreate the 'axis' objects
        self.axis_x = axis.axis(axis_x.coordsEdges) if deepCopy else axis_x
        self.axis_y = axis.axis(axis_y.coordsEdges) if deepCopy else axis_y
        self.axis_z = axis.axis(axis_z.coordsEdges) if deepCopy else axis_z

        #store numbers of edges (NOE)
        self.NOE_X = self.axis_x.noEdges
        self.NOE_Y = self.axis_y.noEdges
        self.NOE_Z = self.axis_z.noEdges

        #store number of cells (NOC)
        self.NOC_X = self.axis_x.noCells
        self.NOC_Y = self.axis_y.noCells
        self.NOC_Z = self.axis_z.noCells

    def createSubset(self, coordsStart, coordsStop):
        r"""Returns a new 'grid3D' which is a subset of the original one

        This method creates and returns a new 'grid3D' object that is a subset
        of the original object. It uses the 'createSubset' method of its 'axis'
        objects to create new sub-axes and then returns a new 'grid3D'
        initialized with those axes. The 'coordsStart' and 'coordsStop'
        parameters contain the coordinates at which the subset is created with
        'coordStart' containing the x, y, and z coordinates the subset starts
        from and 'coordsStop', the coordinates where it ends. These needn't be
        exact coordinates, the nearest ones will be found. These parameters may
        either be 'pointCart3D' objects, lists, or tuples.

        Parameters:
            coordsStart (pointCart3D, list, or tuple): The x, y, and z
                coordinates	where the subset will start from
            coordsStop (pointCart3D, list, or tuple): The x, y, and z
                coordinates wthe subset will stop at

        Returns:
            A new 'grid3D' object where the x, y, and z axes are subsets of the
            original object
        """

        #convert the given coordinates
        coordsStart = point.pointCart3D(coordsStart)
        coordsStop = point.pointCart3D(coordsStop)

        #call the 'createSubset' method of each axis and create a new sub-axis
        sub_axis_x = self.axis_x.createSubset(coordsStart.x, coordsStop.x)
        sub_axis_y = self.axis_y.createSubset(coordsStart.y, coordsStop.y)
        sub_axis_z = self.axis_z.createSubset(coordsStart.z, coordsStop.z)

        #create and return a new 'grid3D' object that is a subset of the
        #original
        return grid3D(sub_axis_x, sub_axis_y, sub_axis_z)

    def shiftGrid(self, coordsShift):
        r"""Shifts the object's 'axis' data by 'coordsShift'

        This method uses the 'shiftAxis' method of its 'axis' objects to shift
        them by 'coordsShift' which is either a 'pointCart3D', a list, a tuple,
        or a numpy.ndarray object containing the x, y, and z coordinates shifts
        the 'grid3D' is shifted by

        Parameters:
            coordsShift (pointCart3D, list, tuple, or numpy.ndarray): The
                coordinates the grid is shifted by
        """

        #convert the given coordinates
        coordsShift = point.pointCart3D(coordsShift)

        self.axis_x.shiftAxis(coordsShift.x)
        self.axis_y.shiftAxis(coordsShift.y)
        self.axis_z.shiftAxis(coordsShift.z)

    def isCoordsInEdgeBounds(self, coords):
        r"""Checks if 'coords' is within the 'edge' bounds

        This method uses the 'isCoordInEdgeBounds' method of its 'axis' objects
        to check whether 'coords' is within the grid's 'edge' bounds. The
        'coords' parameter may be a 'pointCart3D', a list, a tuple, or a
        numpy.ndarray object containing the x, y, and z coordinates to be
        evaluated

        Parameters:
            coords (pointCart3D, list, tuple, or numpy.ndarray): The
                coordinates to be evaluated

        Returns:
            "True" if 'coords' are within the bounds and "False" if not
        """

        #convert the given coordinates
        coords = point.pointCart3D(coords)

        if (self.axis_x.isCoordInEdgeBounds(coords.x) and
            self.axis_y.isCoordInEdgeBounds(coords.y) and
            self.axis_z.isCoordInEdgeBounds(coords.z)):
            return True

        return False

    def isCoordsInCenterBounds(self, coords):
        r"""Checks if 'coords' is within the 'center' bounds

        This method uses the 'isCoordInEdgeBounds' method of its 'axis' objects
        to check whether 'coords' is within the grid's 'center' bounds. The
        'coords' parameter may be a 'pointCart3D', a list, a tuple, or a
        numpy.ndarray object containing the x, y, and z coordinates to be
        evaluated

        Parameters:
            coords (pointCart3D, list, tuple, or numpy.ndarray): The
                coordinates to be evaluated

        Returns:
            "True" if 'coords' are within the bounds and "False" if not
        """

        #convert the given coordinates
        coords = point.pointCart3D(coords)

        if (self.axis_x.isCoordInCenterBounds(coords.x) and
            self.axis_y.isCoordInCenterBounds(coords.y) and
            self.axis_z.isCoordInCenterBounds(coords.z)):
            return True

        return False

    def findCoordsEdgeIdx(self, coords):
        r"""Finds the nearest cell edge indices for given 'coords'

        This method uses the 'findCoordEdgeIdx' method of its 'axis' objects to
        find and return the indices of the nearest existing cell edge
        coordinates on the grid

        Parameters:
            coords (pointCart3D, list, tuple, or numpy.ndarray): The
                coordinates for which the edge indices are found

        Returns:
            A 'idx.idx3D' object containing the found indices
        """

        #convert the given coordinates
        coords = point.pointCart3D(coords)

        i = self.axis_x.findCoordEdgeIdx(coords.x)
        j = self.axis_y.findCoordEdgeIdx(coords.y)
        k = self.axis_z.findCoordEdgeIdx(coords.z)

        return idx.idx3D([i, j, k])

    def findCoordsCenterIdx(self, coords):
        r"""Finds the nearest cell center indices for given 'coords'

        This method uses the 'findCoordEdgeIdx' method of its 'axis' objects to
        find and return the indices of the nearest existing cell center
        coordinates on the grid

        Parameters:
            coords (pointCart3D, list, tuple, or numpy.ndarray): The
                coordinates for which the center indices are found

        Returns:
            A 'idx.idx3D' object containing the found indices
        """

        #convert the given coordinates
        coords = point.pointCart3D(coords)

        i = self.axis_x.findCoordCenterIdx(coords.x)
        j = self.axis_y.findCoordCenterIdx(coords.y)
        k = self.axis_z.findCoordCenterIdx(coords.z)

        return idx.idx3D([i, j, k])

    def getCoordsEdge(self, indices):
        r"""Returns the edge coordinates for given 'indices'

        This method uses the 'indices' and directly accesses the
        'coordsEdges' of the grid's 'axis' objects and returns the actual
        coordinates as a 'pointCart3D' object

        Parameters:
            indices (idx3D, list, tuple, or numpy.ndarray): The
                indices for which the edge coordinates are returned

        Returns:
            A 'point.pointCart3D' object with the found coordinates
        """

        #convert the given indices
        indices = idx.idx3D(indices)

        #get the x, y, and z coordinates for the given indices
        x = self.axis_x.coordsEdges[indices.i]
        y = self.axis_y.coordsEdges[indices.j]
        z = self.axis_z.coordsEdges[indices.k]

        return point.pointCart3D([x, y, z])

    def getCoordsCenter(self, indices):
        r"""Returns the center coordinates for given 'indices'

        This method uses the 'indices' and directly accesses the
        'coordsCenters' of the grid's 'axis' objects and returns the actual
        coordinates as a 'pointCart3D' object

        Parameters:
            indices (idx3D, list, tuple, or numpy.ndarray): The
                indices for which the edge coordinates are returned

        Returns:
            A 'point.pointCart3D' object with the found coordinates
        """

        #convert the given indices
        indices = idx.idx3D(indices)

        #get the x, y, and z coordinates for the given indices
        x = self.axis_x.coordsCenters[indices.i]
        y = self.axis_y.coordsCenters[indices.j]
        z = self.axis_z.coordsCenters[indices.k]

        return point.pointCart3D([x, y, z])

    def getCoordsBounds(self):
        r"""Returns the coordinates of the grid's boundaries

        This method returns two sets of coordinates representing the corners
        of the grid. These coordinates are the first and last edges of the grid
        along the respective axes.

        Returns:
            coordsStart (pointCart3D): The xStart, yStart, and zStart edge
                coordinates
            coordsStop (pointCart3D): The xStop, yStop, and zStop edge
                coordinates
        """

        coordsStart = point.pointCart3D([self.axis_x.coordsEdges[0],
                                        self.axis_y.coordsEdges[0],
                                        self.axis_z.coordsEdges[0]])
        coordsStop = point.pointCart3D([self.axis_x.coordsEdges[-1],
                                        self.axis_y.coordsEdges[-1],
                                        self.axis_z.coordsEdges[-1]])

        return coordsStart, coordsStop

    def createMeshEdges(self):
        r"""Creates and returns an edge coordinate mesh"""

        #create and return the edge coordinate mesh
        mesh = ndmesh(self.axis_x.coordsEdges,
                      self.axis_y.coordsEdges,
                      self.axis_z.coordsEdges)

        #transpose each mesh (to abide by the x-y-z order)
        mesh[0] = mesh[0].transpose()
        mesh[1] = mesh[1].transpose()
        mesh[2] = mesh[2].transpose()

        return mesh

    def createMeshCenters(self):
        r"""Creates and returns an center coordinate mesh"""

        #create and return the center coordinate mesh
        mesh = ndmesh(self.axis_x.coordsCenters,
                      self.axis_y.coordsCenters,
                      self.axis_z.coordsCenters)

        #transpose each mesh (to abide by the x-y-z order)
        mesh[0] = mesh[0].transpose()
        mesh[1] = mesh[1].transpose()
        mesh[2] = mesh[2].transpose()

        return mesh

    def calcCellVolumes(self):
        r"""Creates and returns an array with the area of each cell"""

        meshWidths = ndmesh(self.axis_x.widths,
                            self.axis_y.widths,
                            self.axis_z.widths)

        return (meshWidths[0] * meshWidths[1] * meshWidths[2]).transpose()

    def createCenterGrid(self):
        r"""Returns a new 'grid3D' where the former centers are now the edges

        This method creates and returns a new 'grid3D' object where the current
        cell-center coordinates are the edges in this new grid. Essentially this
        method removes half a layer of cells from around the grid.

        Returns:
            gridNew (grid.grid3D): The new cell-centers grid
        """

        axis_x_new = axis.axis(self.axis_x.coordsCenters)
        axis_y_new = axis.axis(self.axis_y.coordsCenters)
        axis_z_new = axis.axis(self.axis_z.coordsCenters)

        gridNew = grid3D(axis_x_new,
                         axis_y_new,
                         axis_z_new)

        return gridNew

    def createExtended(self, noCellsX, noCellsY, noCellsZ):
        r"""Returns a new extended grid

        This method creates and returns a new 'grid3D' object which has been
        extended in all directions by a number of cells (either the same for
        both directions or different) and the cell-width which is replicated
        from the nearest cell (to the direction of the extension).

        Note:
            This method is a simple wrapper around the 'createExtended' method
            in the axis.axis class. That function offers much more extension
            possiblities and complicated should be done by manually extending
            each axis through that method and then manually creating a new grid.

        Parameters:
            noCellsX (int, list, or tuple): The number of cells to extend the
                axis X by. Should either be a single integer or a list/tuple
                with the number of cells extension happens with in the
                left/right direction.
            noCellsY (int, list, or tuple): The number of cells to extend the
                axis Y by. Should either be a single integer or a list/tuple
                with the number of cells extension happens with in the
                left/right direction.
            noCellsZ (int, list, or tuple): The number of cells to extend the
                axis Z by. Should either be a single integer or a list/tuple
                with the number of cells extension happens with in the
                left/right direction.

        Returns:
            gridNew (grid.grid3D): The new extended 'grid3D' object
        """

        axis_x_new = self.axis_x.createExtended("both", noCellsX)
        axis_y_new = self.axis_y.createExtended("both", noCellsY)
        axis_z_new = self.axis_z.createExtended("both", noCellsZ)

        gridNew = grid3D(axis_x_new,
                         axis_y_new,
                         axis_z_new)

        return gridNew

    def isCartesian(self, error=1.0e-6):
        r"""Checks whether the grid is cartesian

        This method checks whether the current grid is cartesian, i.e., whether
        the cells widths are equal and whether all cells have the same widths
        (i.e., whether the grid is regular).

        Parameters:
            error (float, optional): The maximum allowed difference between
                cell widths in order for them to be considered equal. Defaults
                to "1.0e-6"

        Returns:
            isUni (bool): "True" if the grid is cartesian and "False" otherwise
        """

        #get the widths of the first cell on each axis
        w0x = self.axis_x.widths[0]
        w0y = self.axis_y.widths[0]
        w0z = self.axis_z.widths[0]

        #check the first widths of the different axes
        if abs(w0x - w0y) > error or abs(w0y - w0z) > error:
            return False

        return self.isRegular()

    def isRegular(self, error=1.0e-6):
        r"""Checks whether the grid is regular

        This method checks whether the current grid is regular, i.e., whether
        the cell widths along each axis (but between axes) are equal.

        Parameters:
            error (float, optional): The maximum allowed difference between
                cell widths in order for them to be considered equal. Defaults
                to "1.0e-6"

        Returns:
            isUni (bool): "True" if the grid is regular and "False" otherwise
        """

        #get the widths of the first cell on each axis
        w0x = self.axis_x.widths[0]
        w0y = self.axis_y.widths[0]
        w0z = self.axis_z.widths[0]

        #check for regularity along each axis
        if not ((numpy.abs(self.axis_x.widths - w0x).max() <= error) and
                (numpy.abs(self.axis_y.widths - w0y).max() <= error) and
                (numpy.abs(self.axis_z.widths - w0z).max() <= error)):
            return False

        return True