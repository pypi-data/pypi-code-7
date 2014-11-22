from __future__ import division
import scipy.ndimage.filters as filters
import scipy.ndimage.morphology as morphology
import numpy
import pandas

from fieldpy.primitives.idx import idx2D, idx3D
from fieldpy.primitives.datafield import datafield2D, datafield3D


class locEx(object):
    r"""A single local extreme class

    This class is meant to act as a structure that holds the properties of a
    local extreme. These properties are filled during the extraction of
    such extrema with the 'locExExtractor' class.

    This object may represent either 2D or 3D local extrema depending on
    the type of datafield the extraction was performed on.

    Attributes:
        _type(locEx.type): The type (2D/3D) of the local extreme
        id (int): The ID of the local extreme as assigned during extraction
        coords (pointCart2D or pointCart3D): The coordinates of the extreme's
            location in the datafield the extraction was performed
        index (idx2D or idx3D): The indices of the extreme's location in the
            datafield the extraction was performed
        value (float): The value of the local extreme
    """

    class type: #an enumeration defining the conCo type (2D or 3D)
        e2D, e3D = range(2)

    def __init__(self):
        r"""Class constructor and initialization"""

        self._type = None
        self.id = 0
        self.coords = None
        self.index = None
        self.value = 0.0

    def __repr__(self):
        r"""Returns a string representation of the object"""

        strRepr = "Local Extreme (ID: " + str(self.id) + "):" + "\n"
        strRepr += "\t " + "Value: " + str(self.value) + "\n"
        strRepr += "\t " + "Coordinates: " + str(self.coords) + "\n"
        strRepr += "\t " + "Index:" + str(self.index) + "\n"

        return strRepr

    def getPDFcolumns(self):
        r"""Returns a list of column names to be used in panda.DataFrame objects

        This method creates a list of strings named after each attribute of a
        local extreme object. This list is meant to be used when creating
        a new pandas.DataFrame object in order to easily create and set the
        column names and their values.

        Note:
            Depending on the 'type' of the extreme (i.e., 2D or 3D) the
            returned lists differ

        Returns:
            cols (list): A list of strings matching the names of the locEx
                attributes
        """

        if self._type == locEx.type.e3D:
            cols = ['coords.x',
                    'coords.y',
                    'coords.z',
                    'index.i',
                    'index.j',
                    'index.k',
                    'value']
        else:
            cols = ['coords.x',
                    'coords.y',
                    'index.i',
                    'index.j',
                    'value']

        return cols

class locExExtractor(object):
    r"""

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

    @staticmethod
    def _detect_local_minima(arr, connectivity):
        r"""
        Takes an array and detects the troughs using the local maximum filter.
        Returns a boolean mask of the troughs (i.e. 1 when
        the pixel's value is the neighborhood maximum, 0 otherwise)

        source: http://stackoverflow.com/questions/3684484/peak-detection-in-a-2d
        -array/3689710#3689710
        """
        # define an connected neighborhood
        # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology
        # .html#generate_binary_structure
        neighborhood = morphology.generate_binary_structure(len(arr.shape),
                                                            connectivity)
        # apply the local minimum filter; all locations of minimum value
        # in their neighborhood are set to 1
        # http://www.scipy.org/doc/api_docs/SciPy.ndimage.filters
        # .html#minimum_filter
        local_min = (filters.minimum_filter(arr,
                                            footprint=neighborhood) == arr)
        # local_min is a mask that contains the peaks we are
        # looking for, but also the background.
        # In order to isolate the peaks we must remove the background from the
        # mask.

        # we create the mask of the background
        background = (arr == 0)

        # a little technicality: we must erode the background in order to
        # successfully subtract it from local_min, otherwise a line will
        # appear along the background border (artifact of the local minimum filter)
        # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology
        # .html#binary_erosion
        eroded_background = morphology.binary_erosion(background,
                                                      structure=neighborhood,
                                                      border_value=1)
        #
        # we obtain the final mask, containing only peaks,
        # by removing the background from the local_min mask
        detected_minima = local_min - eroded_background

        #return the minima and their locations
        return detected_minima, numpy.where(detected_minima)

    def extractExtrema(self,
                       strType,
                       connectivity=None,
                       thresholdLow=None,
                       thresholdHigh=None):
        r"""Extract local extrema from a datafield

        This method performs the extraction of local extrema (either maxima or
        minima depending on 'strType') for given thresholds and returns a list
        of 'locEx' objects with appropriately set attributes.

        Parameters:
            strType (str): Should either be 'max' to extract maxima or 'min' to
                extract minima.
            connectivity(int, optional): The neighborhood size used when
                extracting the extrema. By default this is set to the rank of
                the datafield (i.e., "2" for 2D datafields and "3" for 3D)
                during the extraction. Defaults to "None".
            thresholdLow (float, optional): The lower threshold applied before
                the extraction. All array entries below this threshold will not
                be considered during the process. Defaults to "None" in which
                case no thresholding is performed.
            thresholdHigh (float, optional): The upper threshold applied before
                the extraction. All array entries above this threshold will not
                be considered during the process. Defaults to "None" in which
                case no thresholding is performed.

        Returns:
            lstLocEx (list): A list of all the 'locEx' objects extracted during
            this process.
        """

        #check the extraction type
        if not (strType == "max" or strType == "min"):
            raise ValueError("Invalid extraction 'strType' provided")

        #create a private copy of the array
        _arr = self.datafield.dataArray.copy()

        #threshold the array (if required)
        if thresholdLow is not None:
            _arr[(_arr < thresholdLow)] = 0.0
        if thresholdHigh is not None:
            _arr[(_arr > thresholdHigh)] = 0.0

        if connectivity is None:
            connectivity = 2 if self._mode == self.mode.e2D else 3

        if strType == "max":
            _extrema, _extremaLocs = self._detect_local_minima(-1.0 * _arr,
                                                               connectivity)
        else:
            _extrema, _extremaLocs = self._detect_local_minima(_arr,
                                                               connectivity)

        #create empty lists that will contain the extracted extrema
        lstLocEx = []

        #fill the lists with the extrema data
        for i in range(len(_extremaLocs[0])): #loop through extrema locations
            _locex = locEx()
            _locex.id = i
            if self._mode == self.mode.e2D:
                #set the extreme type
                _locex._type = locEx.type.e2D

                #get the indices
                _locex.index = idx2D([_extremaLocs[0][i],
                                      _extremaLocs[1][i]])
                #get the data value
                _locex.value =  self.datafield.dataArray[_locex.index.i,
                                                         _locex.index.j]
            else:
                #set the extreme type
                _locex._type = locEx.type.e3D

                _locex.index = idx3D([_extremaLocs[0][i],
                                      _extremaLocs[1][i],
                                      _extremaLocs[2][i]])
                #get the data value
                _locex.value =  self.datafield.dataArray[_locex.index.i,
                                                         _locex.index.j,
                                                         _locex.index.k]
            #get and append the coordinates
            _locex.coords = self.datafield.dataGrid.getCoordsEdge(_locex.index)
            lstLocEx.append(_locex)

        #returned the extracted data
        return lstLocEx, _extrema

class locExAnalyzer(object):
    r"""A class used to analyze extrema

    This class can be used to analyze extrema as extracted with the
    'locExExtractor' class. Methods to find the peak-valued extreme or the
    extreme nearest to a point are available. In addition, methods to export
    the extrema data into a pandas.DataFrame are also available.

    Attributes:
        lstLocEx (list): a list of 'locEx' objects as extracted by the
            'locExExtractor' class.
    """

    class mode: #an enumeration defining the analysis mode (2D or 3D)
        e2D, e3D = range(2)

    def __init__(self, lstLocEx):
        r"""Class constructor and initialization

        Parameters:
            lstConCos (list): a list of 'conCo' objects as extracted by the
                'conCoExtractor' class.
        """

        if lstLocEx == []:
            raise ValueError("Empty extrema list provided")

        if lstLocEx[0]._type == locEx.type.e2D:
            self._mode = self.mode.e2D
        elif lstLocEx[0]._type == locEx.type.e3D:
            self._mode = self.mode.e3D
        else:
            raise ValueError("Invalid connected components provided")

        #store the list of extrema
        self.lstLocEx = lstLocEx

    def createDataFrame(self):
        r"""Create a pandas.DataFrame with the extrema data

        This method creates and returns a 'pandas.DataFrame' object containing
        the information stored in the 'locEx' objects provided to the class.

        Note:
            The DataFrame index is based on the IDs of the components.

        Returns:
            A 'pandas.DataFrame' object with the extrema information
        """

        #create an empty dataframe with the appropriate columns
        locExDF = pandas.DataFrame(data=None,
                                   index=range(0, len(self.lstLocEx)),
                                   columns=self.lstLocEx[0].getPDFcolumns())

        #fill-in the dataframe with the extrema values
        for locex in self.lstLocEx: #loop through the extrema
            for col in locExDF.columns: #loop through the columns
                #use on-the-fly evaluation to assign the values based on the
                #column name which matches the object attribute
                locExDF.ix[locex.id, col] = eval("locex." + str(col))

        #return the created dataframe
        return locExDF

    def findNearest(self, p):
        r"""Finds and returns the extreme nearest to a point and its distance

        This method loops through all extrema stored in the object
        'lstLocEx' and returns the extreme with the minimum distance to a
        point under the 'p' parameter.

        Paremeters:
            p (pointCart2D or pointCart3D): The point for which the
                distance is calculated

        Returns:
            distNearest (float): The nearest distance found
            locExNearest (locEx): The nearest extreme found
        """

        #empty locEx placeholder
        locExNearest = None
        distNearest = float("inf") #ficticious infinite distance

        #loop through all extrema and find the one with the minimum distance
        for locex in self.lstLocEx:
            dist = abs(locex.coords - p)
            if dist < distNearest:
                locExNearest = locex
                distNearest = dist

        return distNearest, locExNearest

    def findMaximum(self):
        r"""Finds and returns the maximum extreme

        This method loops through all extrema stored in the object
        'lstLocEx' and returns the extreme with the maximum 'value'.

        Returns:
            locExMax (locEx): The maximum extreme found
        """

        #empty component placeholder
        locExMax = None
        valMax = -float("inf") #ficticious value

        #loop through all extrema and find the one with the maximum 'value'
        for locex in self.lstLocEx:
            if locex.value > valMax:
                locExMax = locex
                valMax = locex.value

        return locExMax

    def findMinimum(self):
        r"""Finds and returns the minimum extreme

        This method loops through all extrema stored in the object
        'lstLocEx' and returns the extreme with the minimum 'value'.

        Returns:
            locExMin (locEx): The minimum extreme found
        """

        #empty component placeholder
        locExMin = None
        valMin = float("inf") #ficticious value

        #loop through all extrema and find the one with the minimum 'value'
        for locex in self.lstLocEx:
            if locex.value < valMin:
                locExMin = locex
                valMin = locex.value

        return locExMin

    def findClosestValue(self, val):
        r"""Finds and returns the extreme with the closest 'value' to 'val'

        This method loops through all extrema stored in the object
        'lstLocEx' and returns the extreme with a 'value' closest to the 'val'
        parameter and the absolute difference in values.

        Parameters:
            val (float): The value to which the extreme with the closest
                'value' will be returned

        Returns:
            diffClosest (float): The absolute nearest value difference found
            locExClosest (locEx): The closest extreme found
        """

        #empty locEx placeholder
        locExClosest = None
        diffClosest = float("inf") #ficticious infinite distance

        #loop through all extrema and find the one with the minimum distance
        for locex in self.lstLocEx:
            diff = abs(locex.value - val)
            if diff < diffClosest:
                locExClosest = locex
                diffClosest = diff

        return diffClosest, locExClosest

    def findBestV2D(self,
                    p,
                    weightValue = 1.0,
                    weightDistance = 1.0,
                    maxDistance = float("inf"),
                    minValue = -float("inf")):
        r"""Finds and returns the extreme with the best value/distance ratio

        This method loops through all extrema stored in the object
        'lstLocEx' and returns the extreme with the highest ratio of its value
        to the distance of that extreme from a point 'p'. Weights can be
        assigned to the value (numerator) and distance (denominator). The
        maximum valid distance and minimum valid value can also be assigned.

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
            locExBest (locEx): The best extreme found
        """

        #empty locEx placeholder
        locExBest = None
        v2dBest = -float("inf") #ficticious value

        #loop through all extrema and find the one with the maximum V/D
        for locex in self.lstLocEx:
            dist = abs(locex.coords - p)
            v2d = (weightValue*locex.value)/(weightDistance*dist)
            if v2d > v2dBest:
                if dist < maxDistance and locex.value > minValue:
                    locExBest = locex
                    v2dBest = v2d

        return v2dBest, locExBest