"""
This module contains classes for connected component analysis of a datafield
"""

from __future__ import division
import scipy.ndimage.measurements
import numpy
import pandas

from fieldpy.primitives.point import pointCart2D, pointCart3D
from fieldpy.primitives.idx import idx2D, idx3D
from fieldpy.primitives.datafield import datafield2D, datafield3D


class conCo(object):
    r"""A single connected-component class

    This class is meant to act as a structure that holds the properties of a
    connected component. These properties are filled during the extraction of
    such components with the 'conCoExtractor' class.

    This object may represent either 2D or 3D connected components depending on
    the type of datafield the extraction was performed on.

    Attributes:
        _type (conCo.type): The type (2D/3D) of the component
        id (int): The ID of the connected component as labeled during the
            extraction.
        bbBoordsP0 (pointCart2D or pointCart3D): The coordinates of the
            component's bounding box's first point in the datafield the
            extraction was performed.
        bbBoordsP1 (pointCart2D or pointCart3D): The coordinates of the
            component's bounding box's second point in the datafield the
            extraction was performed.
        bbIdxsP0 (idx2D or idx3D): The indices of the
            component's bounding box's first point in the datafield the
            extraction was performed.
        bbIdxsP1 (idx2D or idx3D): The indices of the
            component's bounding box's second point in the datafield the
            extraction was performed.
        centerCoords (pointCart2D or pointCart3D): The coordinates of the
            component's bounding box's center.
        bbSize (pointCart2D or pointCart3D): The size of the component's
            bounding box.
        AV (float): The area or volume of the connected component (depending on
            its dimensionality) which is calculated as the sum of the
            areas/volumes of all the pixels/voxels the component consists of.
        valMin (float): The minimum value (as existing in the original, non-
            thresholded array of the datafield) within the component
        valMax (float): The maximum value (as existing in the original, non-
            thresholded array of the datafield) within the component
        valMean (float): The mean value (as existing in the original, non-
            thresholded array of the datafield) of the entire component
        valStd (float): The standard deviation value (as existing in the
            original, non-thresholded array of the datafield) of the entire
            component
        valMean (float): The sum value (as existing in the original, non-
            thresholded array of the datafield) of the entire component
        mask (numpy.ndarray): A boolean array with the same shape as the
            datafield's data array acting as a mask for the given component.
            Every "True" entry in this array denotes a pixel/voxel belonging to
            this component.
    """

    class type: #an enumeration defining the conCo type (2D or 3D)
        e2D, e3D = range(2)

    def __init__(self):
        r"""Class constructor and initialization"""

        self._type = None
        self.id = 0 #the component id
        self.bbCoordsP0 = None
        self.bbCoordsP1 = None
        self.bbIdxsP0 = None
        self.bbIdxsP1 = None
        self.centerCoords = None
        self.bbSize = None
        self.AV = 0.0 #area or volume depending on the dimensionality
        self.valMin = 0.0
        self.valMax = 0.0
        self.valMean = 0.0
        self.valStd = 0.0
        self.valSum = 0.0
        self.mask = None

    def __repr__(self):
        r"""Returns a string representation of the object"""

        strRepr = "Connected Component (ID: " + str(self.id) + "):" + "\n"
        strRepr += "\t " + "Values: " + "\n"
        strRepr += "\t\t " + "Max: " + str(self.valMax) + "\n"
        strRepr += "\t\t " + "Min: " + str(self.valMin) + "\n"
        strRepr += "\t\t " + "Mean: " + str(self.valMean) + "\n"
        strRepr += "\t\t " + "STD: " + str(self.valStd) + "\n"
        strRepr += "\t\t " + "Sum: " + str(self.valSum) + "\n"
        strRepr += "\t " + "Size: " + str(self.bbSize) + "\n"
        strRepr += "\t " + "Center Coordinates: " + str(self.centerCoords) + "\n"
        strRepr += "\t " + "Bounding Box Coordinates:" + "\n"
        strRepr += "\t\t " + "P0: " + str(self.bbCoordsP0) + "\n"
        strRepr += "\t\t " + "P1: " + str(self.bbCoordsP1) + "\n"
        strRepr += "\t " + "Bounding Box Indices:" + "\n"
        strRepr += "\t\t " + "P0: " + str(self.bbIdxsP0) + "\n"
        strRepr += "\t\t " + "P1: " + str(self.bbIdxsP1) + "\n"
        strRepr += "\t " + "Area/Volume: " + str(self.AV) + "\n"

        return strRepr

    def getPDFcolumns(self):
        r"""Returns a list of column names to be used in panda.DataFrame objects

        This method creates a list of strings named after each attribute of a
        connected-component object. This list is meant to be used when creating
        a new pandas.DataFrame object in order to easily create and set the
        column names and their values.

        Note:
            Depending on the 'type' of the component (i.e., 2D or 3D) the
            returned lists differ

        Returns:
            cols (list): A list of strings matching the names of the conCo
                attributes
        """

        if self._type == conCo.type.e3D:
            cols = ['bbCoordsP0.x',
                    'bbCoordsP0.y',
                    'bbCoordsP0.z',
                    'bbCoordsP1.x',
                    'bbCoordsP1.y',
                    'bbCoordsP1.z',
                    'bbIdxsP0.i',
                    'bbIdxsP0.j',
                    'bbIdxsP0.k',
                    'bbIdxsP1.i',
                    'bbIdxsP1.j',
                    'bbIdxsP1.k',
                    'centerCoords.x',
                    'centerCoords.y',
                    'centerCoords.z',
                    'bbSize.x',
                    'bbSize.y',
                    'bbSize.z',
                    'AV',
                    'valMin',
                    'valMax',
                    'valMean',
                    'valStd',
                    'valSum']
        else:
            cols = ['bbCoordsP0.x',
                    'bbCoordsP0.y',
                    'bbCoordsP1.x',
                    'bbCoordsP1.y',
                    'bbIdxsP0.i',
                    'bbIdxsP0.j',
                    'bbIdxsP1.i',
                    'bbIdxsP1.j',
                    'centerCoords.x',
                    'centerCoords.y',
                    'bbSize.x',
                    'bbSize.y',
                    'AV',
                    'valMin',
                    'valMax',
                    'valMean',
                    'valStd',
                    'valSum']

        return cols

class conCoExtractor(object):
    r"""A class used to extract connected-components

    This class can be used to extracted connected-components from a 2D or 3D
    'datafield' and return a list of 'conCo' objects representing these
    components.
    """

    class mode: #an enumeration defining the extraction mode (2D or 3D)
        e2D, e3D = range(2)

    def __init__(self, datafield):
        r"""Class constructor and initialization

        Parameters:
            datafield(datafield2D or datafield3D): The datafield the extraction
                is performed on
        """

        #set the extraction mode depending on the type of datafield provided
        if isinstance(datafield, datafield2D):
            self._mode = self.mode.e2D
        elif isinstance(datafield, datafield3D):
            self._mode = self.mode.e3D
        else:
            raise TypeError("Invalid 'datafield' provided")

        #store the datafield
        self.datafield = datafield

    def extractConCos(self,
                      thresholdLow,
                      thresholdHigh,
                      calcAVs=True,
                      storeMasks=True):
        r"""Extract connected-components from a datafield

        This method performs the extraction of connected-components for given
        thresholds and returns a list of 'conCo' objects with appropriately
        set attributes.

        Note:
            The characteristics of the connected-components will depend on the
            choice of threshold as that parameter will define the presence,
            size, values, etc. of those components.

        Parameters:
            thresholdLow (float): The lower threshold applied before the
                extraction. All array entries below this threshold will not
                be considered during the process.
            thresholdHigh (float): The upper threshold applied before the
                extraction. All array entries over this threshold will not
                be considered during the process.
            calcAVs (bool, optional): If set to "True" then the areas/volumes of
                the different components will be calculated (required additional
                calculations). This quantity is the actual area/volume of the
                component and not that of the bounding box. Defaults to "True".
            storeMasks (bool, optional): If set to "True" then boolean masks
                for each individual component will be stored within that object.
                (may result in high memory consumption). Defaults to "True".

        Returns:
            lstConCos (list): A list of all the 'conCo' objects extracted during
            this process.
        """

        # get reference to the array (for brevity's sake)
        _arr = self.datafield.dataArray
        _grid = self.datafield.dataGrid

        # create an empty boolean mask array with the same size as the array
        arrayMask = numpy.zeros(_arr.shape, dtype=numpy.bool)

        # define the mask regions based on the given thresholds
        arrayMask[(_arr >= thresholdLow) * (_arr <= thresholdHigh)] = True

        # label the mask array using scipy
        arrLabeled, noConCo = scipy.ndimage.measurements.label(arrayMask)

        # find the component locations and dimensions using the 'find_objects'
        # method which returns 'slice' objects defining the components
        conCoSlices = scipy.ndimage.measurements.find_objects(arrLabeled)

        #if area/volume calculation is required...
        if calcAVs:
            #get that array from the datafield's 'grid' object
            _arrAV = (self.datafield.dataGrid.calcCellAreas()
                      if self._mode == self.mode.e2D else
                      self.datafield.dataGrid.calcCellVolumes())

        #create an empty list that will contain the conCo objects
        lstConCos = []

        #loop through the number of connected components found
        for concoIdx in range(noConCo):
            conco = conCo() #create a new, empty connected-component

            #set the component's ID (as it exists in the label-field)
            conco.id = concoIdx + 1 # labels start from "1"

            #get the returned 'slice' object for this component
            slices = conCoSlices[concoIdx]

            #check whether the extraction is in 2D or 3D mode
            if self._mode == self.mode.e2D:
                #set the component type
                conco._type = conCo.type.e2D

                #Set the bounding-box indices
                conco.bbIdxsP0 = idx2D([slices[0].start,
                                        slices[1].start])
                conco.bbIdxsP1 = idx2D([slices[0].stop,
                                        slices[1].stop])

                #Set the bounding-box coordinates
                conco.bbCoordsP0 = _grid.getCoordsEdge(conco.bbIdxsP0)
                conco.bbCoordsP1 = _grid.getCoordsEdge(conco.bbIdxsP1)

                #Set the bounding-box center coordinates
                conco.centerCoords = pointCart2D.calcMidPoint(conco.bbCoordsP0,
                                                              conco.bbCoordsP1)
            else:
                #set the component type
                conco._type = conCo.type.e3D

                #Set the bounding-box indices
                conco.bbIdxsP0 = idx3D([slices[0].start,
                                        slices[1].start,
                                        slices[2].start])
                conco.bbIdxsP1 = idx3D([slices[0].stop,
                                        slices[1].stop,
                                        slices[2].stop])

                #Set the bounding-box coordinates
                conco.bbCoordsP0 = _grid.getCoordsEdge(conco.bbIdxsP0)
                conco.bbCoordsP1 = _grid.getCoordsEdge(conco.bbIdxsP1)

                #Set the bounding-box center coordinates
                conco.centerCoords = pointCart3D.calcMidPoint(conco.bbCoordsP0,
                                                              conco.bbCoordsP1)
            #set the bounding box size
            conco.bbSize = conco.bbCoordsP1 - conco.bbCoordsP0

            #create a boolean mask for the particular component
            concoMask = numpy.zeros(_arr.shape, dtype=numpy.bool)
            concoMask[arrLabeled == conco.id] = True

            #set the min/max values of the component
            _arrMasked = _arr[numpy.where(concoMask)]
            conco.valMax = _arrMasked.max()
            conco.valMin = _arrMasked.min()
            conco.valMean = _arrMasked.mean()
            conco.valStd = _arrMasked.std()
            conco.valSum = _arrMasked.sum()

            #store the boolena mask in the component
            if storeMasks:
                conco.mask = concoMask

            #if area/volume calculation is required then set it
            if calcAVs:
                conco.AV = _arrAV[numpy.where(concoMask)].sum()

            #append this new component to the list
            lstConCos.append(conco)

        #return the list of extracted components
        return lstConCos


class conCoAnalyzer(object):
    r"""A class used to analyze connected-components

    This class can be used to analyze connected-components as extracted with the
    'conCoExtractor' class. Methods to find the peak-valued component or the
    component nearest to a point are available. In addition, methods to export
    the component data into a pandas.DataFrame are also available.

    Attributes:
        lstConCos (list): a list of 'conCo' objects as extracted by the
            'conCoExtractor' class.
    """

    class mode: #an enumeration defining the analysis mode (2D or 3D)
        e2D, e3D = range(2)

    def __init__(self, lstConCos):
        r"""Class constructor and initialization

        Parameters:
            lstConCos (list): a list of 'conCo' objects as extracted by the
                'conCoExtractor' class.
        """

        if lstConCos == []:
            raise ValueError("Empty connected-component list provided")

        if lstConCos[0]._type == conCo.type.e2D:
            self._mode = self.mode.e2D
        elif lstConCos[0]._type == conCo.type.e3D:
            self._mode = self.mode.e3D
        else:
            raise ValueError("Invalid connected components provided")

        #store the list of connected-components
        self.lstConCos = lstConCos

    def createDataFrame(self):
        r"""Create a pandas.DataFrame with the connected-component data

        This method creates and returns a 'pandas.DataFrame' object containing
        the information stored in the 'conCo' objects provided to the class.

        Note:
            The DataFrame index is based on the IDs of the components.

        Note:
            Number-based attributes (e.g., coordinates and indices) are included
            int the resulting DataFrame but array-based attributes
            (e.g., boolean masks) are not.

        Returns:
            A 'pandas.DataFrame' object with the component information
        """

        #create an empty dataframe with the appropriate columns
        conCoDF = pandas.DataFrame(data=None,
                                   index=range(1, len(self.lstConCos) + 1),
                                   columns=self.lstConCos[0].getPDFcolumns())

        #fill-in the dataframe with the component values
        for conco in self.lstConCos: #loop through the components
            for col in conCoDF.columns: #loop through the columns
                #use on-the-fly evaluation to assign the values based on the
                #column name which matches the object attribute
                conCoDF.ix[conco.id, col] = eval("conco." + str(col))

        #return the created dataframe
        return conCoDF

    def findNearest(self, p):
        r"""Find and returns the component nearest to a point and its distance

        This method loops through all components stored in the object
        'lstConCos' and returns the component with the minimum distance to a
        point under the 'p' parameter.

        Paremeters:
            p (pointCart2D or pointCart3D): The point for which the distance is
                calculated

        Returns:
            distNearest (float): The nearest distance found
            concoNearest (conCo): The nearest component found
        """

        #empty component placeholder
        concoNearest = None
        distNearest = float("inf") #ficticious infinite distance

        #loop through all components and find the one with the minimum distance
        for conco in self.lstConCos:
            dist = abs(conco.centerCoords - p)
            if dist < distNearest:
                concoNearest = conco
                distNearest = dist

        return distNearest, concoNearest

    def findMaximum(self):
        r"""Find and returns the maximum component

        This method loops through all components stored in the object
        'lstConCos' and returns the component with the maximum 'valMax'.

        Returns:
            concoMax (conCo): The maximum component found
        """

        #empty component placeholder
        concoMax = None
        valMax = -float("inf") #ficticious value

        #loop through all components and find the one with the maximum valMax
        for conco in self.lstConCos:
            if conco.valMax > valMax:
                concoMax = conco
                valMax = conco.valMax

        return concoMax

    def findBestV2D(self,
                    p,
                    weightValue = 1.0,
                    weightDistance = 1.0,
                    maxDistance = float("inf"),
                    minValue = -float("inf")):
        r"""Finds and returns the component with the best value/distance ratio

        This method loops through all components stored in the object
        'lstConCos' and returns the component with the highest ratio of its
        'valMax' to the distance of that component's center from a point 'p'.
        Weights can be assigned to the value (numerator) and distance
        (denominator). The maximum valid distance and minimum valid value can
        also be assigned.

        Paremeters:
            p (pointCart2D or pointCart3D): The point for which the
                distance is calculated
            weightValue (float, optional): The weight the value is multiplied
                by. Defaults to "1.0"
            weightDistance (float, optional): The weight the distance is
                multiplied by. Defaults to "1.0"
            maxDistance (float, optional): The maximum distance that will be
                considered as valid when finding the best extreme. Defaults to
                infinity.
            minValue (float, optional): The minimum value that will be
                considered as valid when finding the best extreme. Defaults to
                -infinity.

        Returns:
            v2dBest (float): The best value/distance ratio found
            concoExBest (conCo): The best component found
        """

        #empty conCo placeholder
        concoBest = None
        v2dBest = -float("inf") #ficticious value

        #loop through all components and find the one with the maximum V/D
        for conco in self.lstConCos:
            dist = abs(conco.centerCoords - p)
            v2d = (weightValue*conco.valMax)/(weightDistance*dist)
            if v2d > v2dBest:
                if dist < maxDistance and conco.valMax > minValue:
                    concoBest = conco
                    v2dBest = v2d

        return v2dBest, concoBest