import numpy
from fieldpy.interpolation import intergrid

def interpolate2D(axis_x,
                  axis_y,
                  array,
                  axis_x_new,
                  axis_y_new,
                  interpOrder=3):

    r"""2D interpolation of an array from one axes set to another

    This function uses the 'intergrid' package and allows for 2D interpolation
    of an array to a uniform or non-uniform grid defined by axes.

    Parameters:
        axis_x (numpy.ndarray): An 1D array containing the coordinates of
            the current array's values along the X axis.
        axis_y (numpy.ndarray): An 1D array containing the coordinates of
            the current array's values along the Y axis.
        array (numpy.ndarray): A 2D array whose shape matches the lengths of the
            provided axes and whose values we mean to resample/interpolate
        axis_x_new (numpy.ndarray): An 1D array containing the coordinates of
            the new array's values along the X axis.
        axis_y_new (numpy.ndarray): An 1D array containing the coordinates of
            the new array's values along the Y axis.
        interpOrder (int, optional): The spline interpolation order which has
            to be between "0" and "5". Defaults to "3"

    Returns:
        array_new (numpy.ndarray): The interpolated version of 'array'
    """

    if not 0<=interpOrder<=5:
        raise ValueError("Invalid interpolation order defined!")

    #create numpy arrays of the array's bounding box's corners
    coordsP0 = numpy.array([axis_x[0], axis_y[0]])
    coordsP1 = numpy.array([axis_x[-1], axis_y[-1]])

    #create a new interpolation function object
    interfunc = intergrid.Intergrid(griddata=array, #the original array
                                    lo=coordsP0, #the lower corner coords
                                    hi=coordsP1, #the upper corner coords
                                    maps=[axis_x, axis_y], #the axes
                                    copy=True, #create a copy of the array
                                    order=interpOrder) #interpolation order

    #create a new product grid based on the interpolation axes
    gridNew = intergrid.productgrid(axis_x_new, axis_y_new)

    #interpolate the array onto the new grid
    array_new = interfunc(gridNew).reshape(len(axis_x_new),
                                           len(axis_y_new))

    #return the interpolated array
    return array_new

def interpolate3D(axis_x,
                  axis_y,
                  axis_z,
                  array,
                  axis_x_new,
                  axis_y_new,
                  axis_z_new,
                  interpOrder=3):

    r"""3D interpolation of an array from one axes set to another

    This function uses the 'intergrid' package and allows for 3D interpolation
    of an array to a uniform or non-uniform grid defined by axes.

    Parameters:
        axis_x (numpy.ndarray): An 1D array containing the coordinates of
            the current array's values along the X axis.
        axis_y (numpy.ndarray): An 1D array containing the coordinates of
            the current array's values along the Y axis.
        axis_z (numpy.ndarray): An 1D array containing the coordinates of
            the current array's values along the Z axis.
        array (numpy.ndarray): A 2D array whose shape matches the lengths of the
            provided axes and whose values we mean to resample/interpolate
        axis_x_new (numpy.ndarray): An 1D array containing the coordinates of
            the new array's values along the X axis.
        axis_y_new (numpy.ndarray): An 1D array containing the coordinates of
            the new array's values along the Y axis.
        axis_z_new (numpy.ndarray): An 1D array containing the coordinates of
            the new array's values along the Z axis.
        interpOrder (int, optional): The spline interpolation order which has
            to be between "0" and "5". Defaults to "3"

    Returns:
        array_new (numpy.ndarray): The interpolated version of 'array'
    """

    if not 0<=interpOrder<=5:
        raise ValueError("Invalid interpolation order defined!")

    #create numpy arrays of the array's bounding box's corners
    coordsP0 = numpy.array([axis_x[0], axis_y[0], axis_z[0]])
    coordsP1 = numpy.array([axis_x[-1], axis_y[-1], axis_z[-1]])

    #create a new interpolation function object
    interfunc = intergrid.Intergrid(griddata=array, #the original array
                                    lo=coordsP0, #the lower corner coords
                                    hi=coordsP1, #the upper corner coords
                                    maps=[axis_x, axis_y, axis_z], #the axes
                                    copy=True, #create a copy of the array
                                    order=interpOrder) #interpolation order

    #create a new product grid based on the interpolation axes
    gridNew = intergrid.productgrid(axis_x_new, axis_y_new, axis_z_new)

    #interpolate the array onto the new grid
    array_new = interfunc(gridNew).reshape(len(axis_x_new),
                                           len(axis_y_new),
                                           len(axis_z_new))

    #return the interpolated array
    return array_new
