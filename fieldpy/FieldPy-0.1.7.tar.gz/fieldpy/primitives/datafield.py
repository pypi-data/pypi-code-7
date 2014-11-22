"""
This module contains datafield primitive classes
"""

from __future__ import division
import numpy
import os

import h5py
import scipy.io

from fieldpy.primitives import ioMHD

from fieldpy.primitives import point
from fieldpy.primitives import axis
from fieldpy.primitives import grid
from fieldpy.primitives import idx


class datafield2D(object):
    r"""A container class for a datafield arranged on a rectilinear grid

    This class acts as a wrapper over a 'grid.grid2D' object and a
    'numpy.ndarray' thus representing a datafield arranged on a rectilinear
    grid. It provides a variety of methods to modify the data and can be used
    with the interpolation and analysis packages.

    Note:
        The data can either lie on the cell centers described by the grid or
        the nodes. This is defined during initialization.

    Attributes:
        dataGrid (grid.grid2D): The 2D rectilinear grid matching the datafield
        dataArray (numpy.ndarray): The 2D numpy array containing the data
    """

    def __init__(self, dataGrid, dataArray, mode, deepCopy=False):
        r"""Class construction and initialization

        This method constructs and initializes the 'datafield2D' object given
        a 'grid.grid2D' and a 'numpy.ndarray' object. The datafield 'mode' can
        also be defined.

        Note:
            The 'mode' defines whether the data lie on the cell centers
            described by the grid or the grid nodes. If the mode is set to
            "center" then the 'dataArray' must be smaller than the grid by 1 in
            every dimension (as the grid defines the edges). If mode is set to
            "node" then the 'dataArray' shape must be the same as the grid's.

        Parameters:
            dataGrid (grid.grid2D): The 2D rectilinear grid matching the
                datafield
            dataArray (numpy.ndarray): The 2D numpy array containing the data
            mode (str): A string defining whether the values in the 'dataArray'
                are lying on the grid centers (mode="center") or nodes (mode=
                "node").
            deepCopy (bool, optional): Whether the provided 'dataGrid' and
                'dataArray' will be deep-copied or not. Defaults to "False"
        """

        if not isinstance(dataGrid, grid.grid2D):
            raise TypeError("The provided 'dataGrid' type is invalid")
        if not isinstance(dataArray, numpy.ndarray):
            raise TypeError("The provided 'dataArray' type is invalid")

        self.dataGrid = (grid.grid2D(dataGrid.axis_x,
                                     dataGrid.axis_y,
                                     deepCopy=True)
                         if deepCopy else dataGrid)
        self.dataArray = dataArray.copy() if deepCopy else dataArray
        self.mode = mode

        if self.mode == "center":
            if not (
                    self.dataGrid.NOC_X,
                    self.dataGrid.NOC_Y) == dataArray.shape:
                raise ValueError(
                    "The 'dataGrid' and 'dataArray' dimensions do not match")
        elif self.mode == "node":
            if not (
                    self.dataGrid.NOE_X,
                    self.dataGrid.NOE_Y) == dataArray.shape:
                raise ValueError(
                    "The 'dataGrid' and 'dataArray' dimensions do not match")
        else:
            raise ValueError("Invalid 'mode' provided")

    def findMaximumIdx(self):
        r"""Find the indices of the maximum value in 'dataArray'

        This method uses numpy's 'argmax' to find the indices of the maximum
        value in the array and 'unravel_index' to transform it to a 2D index
        which it then returns.

        Returns:
            idxMax (idx.idx2D): The 2D index of the maximum in 'dataArray'
        """

        # use numpy to find the max element and then unravel that 1D index into
        #a 2D index
        inds = numpy.unravel_index(self.dataArray.argmax(),
                                   self.dataArray.shape)

        #create a 'idx3D' containing the found indices
        idxMax = idx.idx2D(inds)

        #return the indices
        return idxMax

    def findMaximumCoords(self):
        r"""Find the coordinates of the maximum value in 'dataArray'

        This method uses the 'findMaximumIdx' method to find the indices of the
        maximum in 'dataArray' and returns the coordinates of that point.
        Depending on whether the datafield is in 'center' or 'node' mode the
        appropriate coordinates are returned.

        Returns:
            coordsMax (point.pointCart2D): The 2D coordinates of the maximum in
                'dataArray'
        """

        if self.mode == "node":
            coordsMax = self.dataGrid.getCoordsEdge(self.findMaximumIdx())
        elif self.mode == "center":
            coordsMax = self.dataGrid.getCoordsCenter(self.findMaximumIdx())

        return coordsMax

    def shiftDatafield(self, coordsShift):
        r"""Shifts the datafield's grid by 'coordsShift'

        This method uses the 'shiftGrid' method of its 'dataGrid' object to
        shift it by 'coordsShift' which is either a 'pointCart2D', a list,
        a tuple, or a numpy.ndarray object containing the x and y coordinates
        shifts the 'dataGrid' is shifted by.

        Note:
            This method does not in any way affect 'dataArray'

        Parameters:
            coordsShift (pointCart2D, list, tuple, or numpy.ndarray): The
                coordinates the grid is shifted by
        """

        # shift 'dataGrid'
        self.dataGrid.shiftGrid(coordsShift)

    def shiftToOrigin(self, coordsFrom=None):
        r"""Shifts the datafield's grid from 'coordsFrom' to cartesian origin

        This method uses the 'shiftDatafield' method to shift the 'dataGrid'
        from given coordinates ('coordsFrom') to the cartesian origin point,
        i.e., the (0,0) point. The default behavior shift the datafield's
        maximum's coordinates using the 'findMaximumCoords' method.

        Note:
            This method does not in any way affect 'dataArray'

        Parameters:
            coordsFrom (pointCart2D, list, tuple, or numpy.ndarray, optional):
                The coordinates the grid is shifted from to (0,0). Defaults to
                "None" in which case the location of the maximum is shifted to
                the origin.
        """

        if coordsFrom is None:
            coordsFrom = self.findMaximumCoords()
        else:
            coordsFrom = point.pointCart2D(coordsFrom)

        # shift 'dataGrid'
        self.dataGrid.shiftGrid(coordsFrom * (-1.0))

    def scaleData(self, factor):
        r"""Scales the 'dataArray' by a given 'factor'

        This method multiplies all data in the datafield's 'dataArray' by the
        defined 'factor' float.

        Parameters:
            factor (float): The scaling factor all data in 'dataArray' will be
                multiplied by
        """

        if not isinstance(factor, float):
            raise TypeError("Invalid 'factor' provided. Must be a float.")

        self.dataArray *= factor

    def normalizeData(self, normTo):
        r"""Normalize the 'dataArray' maximum to 'normTo'

        This method first calculates the right normalization factor to scale
        the datafield's 'dataArray' maximum to the value 'normTo', e.g. "1.0".
        It then uses the 'scaleData' method to scale, and therefore, the data.

        Parameters:
            normTo (float): The value the maximum will be normalized to
        """

        if not isinstance(normTo, float):
            raise TypeError("Invalid 'factor' provided. Must be a float.")

        factor = normTo / self.dataArray.max()

        self.scaleData(factor)

    def createSubset(self, coordsStart, coordsStop):
        r"""Returns a new 'datafield2D' which is a subset of the original one

        This method uses the 'createSubset' method of the grid object to create
        and return a subset of the original dataset assuming that valid
        coordinates are provided.

        Parameters:
            coordsStart (pointCart2D, list, or tuple): The x and y coordinates
                where the subset will start from
            coordsStop (pointCart2D, list, or tuple): The x and y coordinates
                where the subset will stop at

        Returns:
            datafield_new (datafield.datafield2D): The new datafield
        """

        # convert the given coordinates
        coordsStart = point.pointCart2D(coordsStart)
        coordsStop = point.pointCart2D(coordsStop)

        #get the truncation indices
        idxStart = self.dataGrid.findCoordsEdgeIdx(coordsStart)
        idxStop = self.dataGrid.findCoordsEdgeIdx(coordsStop)

        #create a new grid and data array
        grid_new = self.dataGrid.createSubset(coordsStart, coordsStop)
        array_new = self.dataArray[idxStart.i:idxStop.i + 1,
                    idxStart.j:idxStop.j + 1]

        #create a new deep-copied datafield
        datafield_new = datafield2D(grid_new,
                                    array_new,
                                    self.mode,
                                    deepCopy=True)

        return datafield_new

    def convertNode2Center(self):
        r"""Creates a centered datafield from a nodal one

        This method creates datafield with mode="center" from a datafield with
        mode="node" (mode conversion). The method uses the 'createCenterGrid'
        and 'createExtended' methods of its grid object to create a new grid
        where the current nodes will be the centers in this new grid. It then
        creates and returns a new datafield with this grid and the existing
        data.

        Returns:
            datafield_new (datafield.datafield2D): The new 'converted'
                datafield
        """

        # check that the mode of the current field is indeed nodal
        if self.mode != "node":
            raise ValueError(
                "The current datafield is not in 'node' mode. This method "
                "only applies to such datafields")

        # create an appropriate grid (centered and extended)
        grid_new = self.dataGrid.createCenterGrid()
        grid_new = grid_new.createExtended(1, 1)

        # create the new converted datafield
        datafield_new = datafield2D(grid_new,
                                    self.dataArray,
                                    mode="center",
                                    deepCopy=True)

        return datafield_new

    def _toHDF5(self, fname, useCompression=True):
        r"""Saves the dataset to an HDF5 file

        This method creates an .h5 file under 'fname' and saves the contents of
        the datafield using the h5py module.

        Parameters:
            fname (str): The filename under which the dataset is saved
        """

        # create new h5 file
        fid = h5py.File(fname, 'w')

        # write axes edge coordinate (in order to later recreate it)
        fid.create_dataset(name="axis_x",
                           shape=self.dataGrid.axis_x.coordsEdges.shape,
                           data=self.dataGrid.axis_x.coordsEdges,
                           compression="gzip" if useCompression else None,
                           compression_opts=9 if useCompression else None)
        fid.create_dataset(name="axis_y",
                           shape=self.dataGrid.axis_y.coordsEdges.shape,
                           data=self.dataGrid.axis_y.coordsEdges,
                           compression="gzip" if useCompression else None,
                           compression_opts=9 if useCompression else None)

        # write dataArray
        dset = fid.create_dataset(name="dataArray",
                                  shape=self.dataArray.shape,
                                  data=self.dataArray,
                                  compression="gzip" if useCompression else None,
                                  compression_opts=9 if useCompression else None)
        # write datafield mode as an attribute of the dataArray dataset
        dset.attrs["mode"] = self.mode

        # flush buffers and close file
        fid.flush()
        fid.close()

    def _toMat(self, fname):
        r"""Saves the dataset to a MATLAB file

        This method creates an .mat file under 'fname' and saves the contents of
        the datafield using the scipy.io module.

        Parameters:
            fname (str): The filename under which the dataset is saved
        """

        # create a dictionary to store the data to be saved
        data = {}

        # adding axes, dataArray, and mode
        data['axis_x'] = self.dataGrid.axis_x.coordsEdges
        data['axis_y'] = self.dataGrid.axis_y.coordsEdges
        data['dataArray'] = self.dataArray
        data['mode'] = self.mode

        # save data
        scipy.io.savemat(fname, data)

    def _toMHD(self, fname):
        r"""Saves the dataset to a MHD file

        This method creates an .mhd file under 'fname' and saves the contents of
        the datafield using the ioMHD module included in this package.

        Note:
            The MHD format only supports regular grids with 'node' mode data.

        Parameters:
            fname (str): The filename under which the dataset is saved
        """

        # define the spacing (regular grid assumed)
        spacing = (self.dataGrid.axis_x.widths[0],
                   self.dataGrid.axis_y.widths[0])

        # define the offset
        offset = (self.dataGrid.axis_x.coordsEdges[0],
                  self.dataGrid.axis_y.coordsEdges[0])

        # write the mhd file
        ioMHD.mhdWrite(fname,
                       self.dataArray,
                       spacing,
                       offset)

    def toFile(self, fname, useCompression=True):
        r"""Saves the dataset to a file

        This method saves the necessary contents of the dataset in order to
        later on load them and recreate it. This includes the edge coordinates
        of the 'axis' objects under the 'dataGrid', the numpy.ndarray under
        'dataArray', and a string containing the 'mode'.

        Note:
            Both HDF5 and MATLAB formats are supported using the h5py and
            scipy.io modules respectively

        Note:
            The MHD format only supports regular grids with 'node' mode data.

        Parameters:
            fname (str): The filename under which the dataset is saved
            useCompression (bool): Whether to use compression or not, when
                supported
        """

        # get the file extension
        strF, strExt = os.path.splitext(fname)
        strFormat = strExt.lower()

        # check the format and call the appropriate private method
        if strFormat == ".h5":
            self._toHDF5(fname, useCompression)
        elif strFormat == ".mat":
            self._toMat(fname)
        elif strFormat == ".mhd":
            if not self.mode == "node":
                raise ValueError(
                    "Only datafields in 'node' mode are supported in MHD "
                    "format")
            self._toMHD(fname)
        else:
            raise ValueError(
                "Invalid format " + strFormat + " or file provided")

    @classmethod
    def _fromHDF5(cls, fname):
        r"""Creates a new datafield from data saved in a HDF5 file

        This method loads the data saved in a .h5 file created with the '_toH5'
        method and creates and returns a new datafield with that data.

        Parameters:
            fname (str): The .h5 filename under which the dataset was saved
        """

        # open the h5 file
        fid = h5py.File(fname, 'r')

        # read in all data
        axis_x = axis.axis(numpy.array(fid['axis_x']))
        axis_y = axis.axis(numpy.array(fid['axis_y']))
        dataArray = numpy.array(fid['dataArray'])
        mode = str(fid['dataArray'].attrs["mode"])

        if "node" in mode:
            mode = "node"
        elif "center" in mode:
            mode = "center"

        # create a new datafield with the loaded data
        df = cls(grid.grid2D(axis_x,
                             axis_y),
                 dataArray,
                 mode,
                 deepCopy=True)

        # close the file
        fid.close()

        return df

    @classmethod
    def _fromMat(cls, fname):
        r"""Creates a new datafield from data saved in a MATLAB file

        This method loads the data saved in a .mat file created with the
        '_toMat' method and creates and returns a new datafield with that data.

        Parameters:
            fname (str): The .mat filename under which the dataset was saved
        """

        # load all .mat data
        data = scipy.io.loadmat(fname)

        # recreate axes
        axis_x = axis.axis(numpy.squeeze(data['axis_x']))
        axis_y = axis.axis(numpy.squeeze(data['axis_y']))

        # load dataArray
        dataArray = numpy.array(data['dataArray'])

        # recreate mode string
        mode = str(data['mode'][0])

        # create new datafield object
        df = cls(grid.grid2D(axis_x,
                             axis_y),
                 dataArray,
                 mode,
                 deepCopy=True)

        return df

    @classmethod
    def _fromMHD(cls, fname):
        r"""Creates a new datafield from data saved in a MHD file

        This method loads the data saved in a .mhd file created with the
        '_toMHD' method and creates and returns a new datafield with that data.

        Parameters:
            fname (str): The .mhd filename under which the dataset was saved
        """

        # read the mhd file
        dataArray, spacing, offset = ioMHD.mhdRead(fname)

        # recreate axes based on the offset and spacing (having assumed
        # regularity during writing the file)
        axis_x = axis.axis(numpy.arange(offset[0],
                                        offset[0] +
                                        spacing[0] * dataArray.shape[0],
                                        spacing[0]))
        axis_y = axis.axis(numpy.arange(offset[1],
                                        offset[1] +
                                        spacing[1] * dataArray.shape[1],
                                        spacing[1]))

        # create new datafield object
        df = cls(grid.grid2D(axis_x,
                             axis_y),
                 dataArray,
                 mode="node",
                 deepCopy=True)

        return df

    @classmethod
    def fromFile(cls, fname):
        r"""Creates a dataset from a file

        This method loads the necessary contents for a dataset saved in a file
        with the 'toFile' method and returns a new dataset with that data.

        Note:
            HDF5, MATLAB, and MHD formats are supported using the h5py, scipy.io
            and the libs.ioMHD modules respectively

        Parameters:
            fname (str): The filename under which the dataset is saved. The
                loaded file must include the appropriate extension in order
                for the correct loading procedure to be used.
        """

        # get the file extension
        strF, strExt = os.path.splitext(fname)
        strFormat = strExt.lower()

        # call the appropriate private method to load the data
        if strFormat == ".h5":
            return cls._fromHDF5(fname)
        elif strFormat == ".mat":
            return cls._fromMat(fname)
        elif strFormat == ".mhd":
            return cls._fromMHD(fname)
        else:
            raise ValueError(
                "Invalid format " + strFormat + " or file provided")


class datafield3D(object):
    r"""A container class for a datafield arranged on a rectilinear grid

    This class acts as a wrapper over a 'grid.grid3D' object and a
    'numpy.ndarray' thus representing a datafield arranged on a rectilinear
    grid. It provides a variety of methods to modify the data and can be used
    with the interpolation and analysis packages.

    Note:
        The data can either lie on the cell centers described by the grid or
        the nodes. This is defined during initialization.

    Attributes:
        dataGrid (grid.grid2D): The 3D rectilinear grid matching the datafield
        dataArray (numpy.ndarray): The 3D numpy array containing the data
    """

    def __init__(self, dataGrid, dataArray, mode, deepCopy=False):
        r"""Class construction and initialization

        This method constructs and initializes the 'datafield3D' object given
        a 'grid.grid3D' and a 'numpy.ndarray' object. The datafield 'mode' can
        also be defined.

        Note:
            The 'mode' defines whether the data lie on the cell centers
            described by the grid or the grid nodes. If the mode is set to
            "center" then the 'dataArray' must be smaller than the grid by 1 in
            every dimension (as the grid defines the edges). If mode is set to
            "node" then the 'dataArray' shape must be the same as the grid's.

        Parameters:
            dataGrid (grid.grid3D): The 3D rectilinear grid matching the
                datafield
            dataArray (numpy.ndarray): The 3D numpy array containing the data
            mode (str): A string defining whether the values in the 'dataArray'
                are lying on the grid centers (mode="center") or nodes (mode=
                "node").
            deepCopy (bool, optional): Whether the provided 'dataGrid' and
                'dataArray' will be deep-copied or not. Defaults to "False"
        """

        if not isinstance(dataGrid, grid.grid3D):
            raise TypeError("The provided 'dataGrid' type is invalid")
        if not isinstance(dataArray, numpy.ndarray):
            raise TypeError("The provided 'dataArray' type is invalid")

        self.dataGrid = (grid.grid3D(dataGrid.axis_x,
                                     dataGrid.axis_y,
                                     dataGrid.axis_z,
                                     deepCopy=True)
                         if deepCopy else dataGrid)
        self.dataArray = dataArray.copy() if deepCopy else dataArray
        self.mode = mode

        if self.mode == "center":
            if not (self.dataGrid.NOC_X, self.dataGrid.NOC_Y,
                    self.dataGrid.NOC_Z) == dataArray.shape:
                raise ValueError(
                    "The 'dataGrid' and 'dataArray' dimensions do not match")
        elif self.mode == "node":
            if not (self.dataGrid.NOE_X, self.dataGrid.NOE_Y,
                    self.dataGrid.NOE_Z) == dataArray.shape:
                raise ValueError(
                    "The 'dataGrid' and 'dataArray' dimensions do not match")
        else:
            raise ValueError("Invalid 'mode' provided")

    def findMaximumIdx(self):
        r"""Find the indices of the maximum value in 'dataArray'

        This method uses numpy's 'argmax' to find the indices of the maximum
        value in the array and 'unravel_index' to transform it to a 3D index
        which it then returns.

        Returns:
            idxMax (idx.idx3D): The 3D index of the maximum in 'dataArray'
        """

        # use numpy to find the max element and then unravel that 1D index into
        #a 3D index
        inds = numpy.unravel_index(self.dataArray.argmax(),
                                   self.dataArray.shape)

        #create a 'idx3D' containing the found indices
        idxMax = idx.idx3D(inds)

        #return the indices
        return idxMax

    def findMaximumCoords(self):
        r"""Find the coordinates of the maximum value in 'dataArray'

        This method uses the 'findMaximumIdx' method to find the indices of the
        maximum in 'dataArray' and returns the coordinates of that point.
        Depending on whether the datafield is in 'center' or 'node' mode the
        appropriate coordinates are returned.

        Returns:
            coordsMax (point.pointCart3D): The 3D coordinates of the maximum in
                'dataArray'
        """

        if self.mode == "node":
            coordsMax = self.dataGrid.getCoordsEdge(self.findMaximumIdx())
        elif self.mode == "center":
            coordsMax = self.dataGrid.getCoordsCenter(self.findMaximumIdx())

        return coordsMax

    def shiftDatafield(self, coordsShift):
        r"""Shifts the datafield's grid by 'coordsShift'

        This method uses the 'shiftGrid' method of its 'dataGrid' object to
        shift it by 'coordsShift' which is either a 'pointCart3D', a list,
        a tuple, or a numpy.ndarray object containing the x and y coordinates
        shifts the 'dataGrid' is shifted by.

        Note:
            This method does not in any way affect 'dataArray'

        Parameters:
            coordsShift (pointCart3D, list, tuple, or numpy.ndarray): The
                coordinates the grid is shifted by
        """

        # shift 'dataGrid'
        self.dataGrid.shiftGrid(coordsShift)

    def shiftToOrigin(self, coordsFrom=None):
        r"""Shifts the datafield's grid from 'coordsFrom' to cartesian origin

        This method uses the 'shiftDatafield' method to shift the 'dataGrid'
        from given coordinates ('coordsFrom') to the cartesian origin point,
        i.e., the (0,0,0) point. The default behavior shift the datafield's
        maximum's coordinates using the 'findMaximumCoords' method.

        Note:
            This method does not in any way affect 'dataArray'

        Parameters:
            coordsFrom (pointCart3D, list, tuple, or numpy.ndarray, optional):
                The coordinates the grid is shifted from to (0,0,0). Defaults to
                "None" in which case the location of the maximum is shifted to
                the origin.
        """

        if coordsFrom is None:
            coordsFrom = self.findMaximumCoords()
        else:
            coordsFrom = point.pointCart3D(coordsFrom)

        # shift 'dataGrid'
        self.dataGrid.shiftGrid(coordsFrom * (-1.0))

    def scaleData(self, factor):
        r"""Scales the 'dataArray' by a given 'factor'

        This method multiplies all data in the datafield's 'dataArray' by the
        defined 'factor' float.

        Parameters:
            factor (float): The scaling factor all data in 'dataArray' will be
                multiplied by
        """

        if not isinstance(factor, float):
            raise TypeError("Invalid 'factor' provided. Must be a float.")

        self.dataArray *= factor

    def normalizeData(self, normTo):
        r"""Normalize the 'dataArray' maximum to 'normTo'

        This method first calculates the right normalization factor to scale
        the datafield's 'dataArray' maximum to the value 'normTo', e.g. "1.0".
        It then uses the 'scaleData' method to scale, and therefore, the data.

        Parameters:
            normTo (float): The value the maximum will be normalized to
        """

        if not isinstance(normTo, float):
            raise TypeError("Invalid 'factor' provided. Must be a float.")

        factor = normTo / self.dataArray.max()

        self.scaleData(factor)

    def createSubset(self, coordsStart, coordsStop):
        r"""Returns a new 'datafield3D' which is a subset of the original one

        This method uses the 'createSubset' method of the grid object to create
        and return a subset of the original dataset assuming that valid
        coordinates are provided.

        Parameters:
            coordsStart (pointCart3D, list, or tuple): The x, y and z
                coordinates where the subset will start from
            coordsStop (pointCart3D, list, or tuple): The x, y, and z
                coordinates where the subset will stop at

        Returns:
            datafield_new (datafield.datafield3D): The new datafield
        """

        # convert the given coordinates
        coordsStart = point.pointCart3D(coordsStart)
        coordsStop = point.pointCart3D(coordsStop)

        #get the truncation indices
        idxStart = self.dataGrid.findCoordsEdgeIdx(coordsStart)
        idxStop = self.dataGrid.findCoordsEdgeIdx(coordsStop)

        #create a new grid and data array
        grid_new = self.dataGrid.createSubset(coordsStart, coordsStop)
        array_new = self.dataArray[idxStart.i:idxStop.i + 1,
                    idxStart.j:idxStop.j + 1,
                    idxStart.k:idxStop.k + 1]

        #create a new deep-copied datafield
        datafield_new = datafield3D(grid_new,
                                    array_new,
                                    self.mode,
                                    deepCopy=True)

        return datafield_new

    def convertNode2Center(self):
        r"""Creates a centered datafield from a nodal one

        This method creates datafield with mode="center" from a datafield with
        mode="node" (mode conversion). The method uses the 'createCenterGrid'
        and 'createExtended' methods of its grid object to create a new grid
        where the current nodes will be the centers in this new grid. It then
        creates and returns a new datafield with this grid and the existing
        data.

        Returns:
            datafield_new (datafield.datafield3D): The new 'converted'
                datafield
        """

        # check that the mode of the current field is indeed nodal
        if self.mode != "node":
            raise ValueError(
                "The current datafield is not in 'node' mode. This method "
                "only applies to such datafields")

        #create an appropriate grid (centered and extended)
        grid_new = self.dataGrid.createCenterGrid()
        grid_new = grid_new.createExtended(1, 1, 1)

        #create the new converted datafield
        datafield_new = datafield3D(grid_new,
                                    self.dataArray,
                                    mode="center",
                                    deepCopy=True)

        return datafield_new

    def _toHDF5(self, fname, useCompression=True):
        r"""Saves the dataset to an HDF5 file

        This method creates an .h5 file under 'fname' and saves the contents of
        the datafield using the h5py module.

        Parameters:
            fname (str): The filename under which the dataset is saved
        """

        # create new h5 file
        fid = h5py.File(fname, 'w')

        # write axes edge coordinate (in order to later recreate it)
        fid.create_dataset(name="axis_x",
                           shape=self.dataGrid.axis_x.coordsEdges.shape,
                           data=self.dataGrid.axis_x.coordsEdges,
                           compression="gzip" if useCompression else None,
                           compression_opts=9 if useCompression else None)
        fid.create_dataset(name="axis_y",
                           shape=self.dataGrid.axis_y.coordsEdges.shape,
                           data=self.dataGrid.axis_y.coordsEdges,
                           compression="gzip" if useCompression else None,
                           compression_opts=9 if useCompression else None)
        fid.create_dataset(name="axis_z",
                           shape=self.dataGrid.axis_z.coordsEdges.shape,
                           data=self.dataGrid.axis_z.coordsEdges,
                           compression="gzip" if useCompression else None,
                           compression_opts=9 if useCompression else None)

        # write dataArray
        dset = fid.create_dataset(name="dataArray",
                                  shape=self.dataArray.shape,
                                  data=self.dataArray,
                                  compression="gzip" if useCompression else None,
                                  compression_opts=9 if useCompression else None)
        # write datafield mode as an attribute of the dataArray dataset
        dset.attrs["mode"] = self.mode

        # flush buffers and close file
        fid.flush()
        fid.close()

    def _toMat(self, fname):
        r"""Saves the dataset to a MATLAB file

        This method creates an .mat file under 'fname' and saves the contents of
        the datafield using the scipy.io module.

        Parameters:
            fname (str): The filename under which the dataset is saved
        """

        # create a dictionary to store the data to be saved
        data = {}

        # adding axes, dataArray, and mode
        data['axis_x'] = self.dataGrid.axis_x.coordsEdges
        data['axis_y'] = self.dataGrid.axis_y.coordsEdges
        data['axis_z'] = self.dataGrid.axis_z.coordsEdges
        data['dataArray'] = self.dataArray
        data['mode'] = self.mode

        # save data
        scipy.io.savemat(fname, data)

    def _toMHD(self, fname):
        r"""Saves the dataset to a MHD file

        This method creates an .mhd file under 'fname' and saves the contents of
        the datafield using the libs.ioMHD module included in this package.

        Note:
            The MHD format only supports regular grids with 'node' mode data.

        Parameters:
            fname (str): The filename under which the dataset is saved
        """

        # define the spacing (regular grid assumed)
        spacing = (self.dataGrid.axis_x.widths[0],
                   self.dataGrid.axis_y.widths[0],
                   self.dataGrid.axis_z.widths[0])

        # define the offset
        offset = (self.dataGrid.axis_x.coordsEdges[0],
                  self.dataGrid.axis_y.coordsEdges[0],
                  self.dataGrid.axis_z.coordsEdges[0])

        # write the mhd file
        ioMHD.mhdWrite(fname,
                       self.dataArray,
                       spacing,
                       offset)

    def toFile(self, fname, useCompression=True):
        r"""Saves the dataset to a file

        This method saves the necessary contents of the dataset in order to
        later on load them and recreate it. This includes the edge coordinates
        of the 'axis' objects under the 'dataGrid', the numpy.ndarray under
        'dataArray', and a string containing the 'mode'.

        Note:
            Both HDF5 and MATLAB formats are supported using the h5py and
            scipy.io modules respectively

        Note:
            The MHD format only supports regular grids with 'node' mode data.

        Parameters:
            fname (str): The filename under which the dataset is saved
            useCompression (bool): Whether to use compression or not, when
                supported
        """

        # get the file extension
        strF, strExt = os.path.splitext(fname)
        strFormat = strExt.lower()

        # check the format and call the appropriate private method
        if strFormat == ".h5":
            self._toHDF5(fname, useCompression)
        elif strFormat == ".mat":
            self._toMat(fname)
        elif strFormat == ".mhd":
            if not self.mode == "node":
                raise ValueError(
                    "Only datafields in 'node' mode are supported in MHD "
                    "format")
            self._toMHD(fname)
        else:
            raise ValueError(
                "Invalid format " + strFormat + " or file provided")

    @classmethod
    def _fromHDF5(cls, fname):
        r"""Creates a new datafield from data saved in a HDF5 file

        This method loads the data saved in a .h5 file created with the '_toH5'
        method and creates and returns a new datafield with that data.

        Parameters:
            fname (str): The .h5 filename under which the dataset was saved
        """

        # open the h5 file
        fid = h5py.File(fname, 'r')

        # read in all data
        axis_x = axis.axis(numpy.array(fid['axis_x']))
        axis_y = axis.axis(numpy.array(fid['axis_y']))
        axis_z = axis.axis(numpy.array(fid['axis_z']))
        dataArray = numpy.array(fid['dataArray'])
        mode = str(fid['dataArray'].attrs["mode"])

        if "node" in mode:
            mode = "node"
        elif "center" in mode:
            mode = "center"

        # create a new datafield with the loaded data
        df = cls(grid.grid3D(axis_x,
                             axis_y,
                             axis_z),
                 dataArray,
                 mode,
                 deepCopy=True)

        # close the file
        fid.close()

        return df

    @classmethod
    def _fromMat(cls, fname):
        r"""Creates a new datafield from data saved in a MATLAB file

        This method loads the data saved in a .mat file created with the
        '_toMat' method and creates and returns a new datafield with that data.

        Parameters:
            fname (str): The .mat filename under which the dataset was saved
        """

        # load all .mat data
        data = scipy.io.loadmat(fname)

        # recreate axes
        axis_x = axis.axis(numpy.squeeze(data['axis_x']))
        axis_y = axis.axis(numpy.squeeze(data['axis_y']))
        axis_z = axis.axis(numpy.squeeze(data['axis_z']))

        # load dataArray
        dataArray = numpy.array(data['dataArray'])

        # recreate mode string
        mode = str(data['mode'][0])

        # create new datafield object
        df = cls(grid.grid3D(axis_x,
                             axis_y,
                             axis_z),
                 dataArray,
                 mode,
                 deepCopy=True)

        return df

    @classmethod
    def _fromMHD(cls, fname):
        r"""Creates a new datafield from data saved in a MHD file

        This method loads the data saved in a .mhd file created with the
        '_toMHD' method and creates and returns a new datafield with that data.

        Parameters:
            fname (str): The .mhd filename under which the dataset was saved
        """

        # read the mhd file
        dataArray, spacing, offset = ioMHD.mhdRead(fname)

        # recreate axes based on the offset and spacing (having assumed
        # regularity during writing the file)
        axis_x = axis.axis(numpy.arange(offset[0],
                                        offset[0] +
                                        spacing[0] * dataArray.shape[0],
                                        spacing[0]))
        axis_y = axis.axis(numpy.arange(offset[1],
                                        offset[1] +
                                        spacing[1] * dataArray.shape[1],
                                        spacing[1]))
        axis_z = axis.axis(numpy.arange(offset[2],
                                        offset[2] +
                                        spacing[2] * dataArray.shape[2],
                                        spacing[2]))

        # create new datafield object
        df = cls(grid.grid3D(axis_x,
                             axis_y,
                             axis_z),
                 dataArray,
                 mode="node",
                 deepCopy=True)

        return df

    @classmethod
    def fromFile(cls, fname):
        r"""Creates a dataset from a file

        This method loads the necessary contents for a dataset saved in a file
        with the 'toFile' method and returns a new dataset with that data.

        Note:
            HDF5, MATLAB, and MHD formats are supported using the h5py, scipy.io
            and the ioMHD modules respectively

        Parameters:
            fname (str): The filename under which the dataset is saved. The
                loaded file must include the appropriate extension in order
                for the correct loading procedure to be used.
        """

        # get the file extension
        strF, strExt = os.path.splitext(fname)
        strFormat = strExt.lower()

        # call the appropriate private method to load the data
        if strFormat == ".h5":
            return cls._fromHDF5(fname)
        elif strFormat == ".mat":
            return cls._fromMat(fname)
        elif strFormat == ".mhd":
            return cls._fromMHD(fname)
        else:
            raise ValueError(
                "Invalid format " + strFormat + " or file provided")