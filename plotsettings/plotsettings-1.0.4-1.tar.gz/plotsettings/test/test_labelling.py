'''
Tests for plot labelling routines

Created on Oct 20, 2014

@author: gdelraye
'''

import numpy
from matplotlib import pyplot
from mpl_toolkits.axes_grid1 import AxesGrid
from plotsettings.set import is_colorbar

def test_colorbardetector():
    '''Test whether the colorbar detecting functionality works for both
    normal subplots (e.g. those created by pyplot) and AxesGrid subplots.
    '''
    # Create test figure
    def bivariate_plot():
        '''Create test data
        '''
        delta = 0.5
        
        extent = (-3,4,-4,3)
        
        x = numpy.arange(-3.0, 4.001, delta)
        y = numpy.arange(-4.0, 3.001, delta)
        X, Y = numpy.meshgrid(x, y)
        Z1 = pyplot.mlab.bivariate_normal(X, Y, 1.0, 1.0, 0.0, 0.0)
        Z2 = pyplot.mlab.bivariate_normal(X, Y, 1.5, 0.5, 1, 1)
        Z = (Z1 - Z2) * 10
        return Z, extent
    # Test colorbar detection with subplots
    fig, ax = pyplot.subplots(1, 1)
    z, extent = bivariate_plot()
    im = ax.imshow(z, extent = extent, origin = 'lower')
    pyplot.colorbar(im)
    axis_list = fig.get_axes()
    axis, colorbar = axis_list
    assert is_colorbar(axis) == False # Main subplot axis is not a colorbar
    assert is_colorbar(colorbar) == True # subplot colorbar axis is a colorbar
    # Test colorbar detection with AxisGrid objects
    fig = pyplot.figure()
    grid = AxesGrid(fig, 111, nrows_ncols = (1, 1), cbar_location = "bottom", cbar_pad = 0.25, cbar_size = "15%")
    im = grid[0].imshow(z, extent = extent, origin = 'lower')
    grid.cbar_axes[0].colorbar(im)
    axis_list = fig.get_axes()
    axis, colorbar = axis_list
    assert is_colorbar(axis) == False # Main AxesGrid axis is not a colorbar
    assert is_colorbar(colorbar) == True # AxesGrid colorbar axis is a colorbar





