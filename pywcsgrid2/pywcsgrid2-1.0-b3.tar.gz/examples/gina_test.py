import matplotlib.pyplot as plt

import astropy.io.fits as pyfits

from mpl_toolkits.axisartist.floating_axes import floatingaxes_class_factory

from pywcsgrid2.axes_wcs import GridHelperWcsFloating, AxesWcs

import matplotlib.axes as maxes

FloatingAxes = floatingaxes_class_factory(AxesWcs)
FloatingSubplot = maxes.subplot_class_factory(FloatingAxes)

def make_allsky_axes_from_header(fig, rect, header, lon_center,
                                 lat_minmax=None, pseudo_cyl=None):


    proj = header["CTYPE1"].split("-")[-1]
    if pseudo_cyl is None:
        if proj in _proj_pseudo_cyl_list:
            pseudo_cyl = True

    if lat_minmax is None:
        lat_max = _proj_lat_limits.get(proj, 90)
        lat_min = -lat_max
    else:
        lat_min, lat_max = lat_minmax

    extremes = (lon_center+180., lon_center-180., lat_min, lat_max)

    grid_helper = GridHelperWcsFloating(wcs=header, extremes=extremes)

    ax = FloatingSubplot(fig, rect, grid_helper=grid_helper)

    return ax

if __name__ == "__main__":

    fig = plt.figure(1)
    rect = 111
    proj = "PAR"
    coord, lon_center = "fk5", 180

    #fig, rect, coord, proj, lon_center=0, lat_minmax=None, pseudo_cyl=None

    from pywcsgrid2.allsky_axes import allsky_header
    header = allsky_header(coord, proj, lon_center)

    ax = make_allsky_axes_from_header(fig, rect, header, lon_center,
                                      pseudo_cyl=False, lat_minmax=(-90, 90))

    gh = ax.get_grid_helper()

    print repr(ax)
    print repr(gh)
    print repr(gh.locator_params)
    print repr(ax.locator_params)
