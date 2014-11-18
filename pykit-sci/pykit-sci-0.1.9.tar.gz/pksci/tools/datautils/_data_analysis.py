# -*- coding: utf-8 -*-
"""
============================================================================
Functions for data analysis (:mod:`pksci.tools.datautils._data_analysis`)
============================================================================

.. currentmodule:: pksci.tools.datautils._data_analysis

.. autosummary::
   :toctree: generated/

   error_bars
   line_eval
   line_fit_residuals
   normalize
   reblock_data
   smooth_data


"""
from __future__ import absolute_import, division, print_function
__docformat__ = 'restructuredtext'

import numpy as np

from .._arrayfuncs import resize_array

__all__ = ['error_bars', 'line_eval', 'line_fit_residuals',
           'normalize', 'reblock_data', 'smooth_data']


def error_bars(data):
    """Calculate or estimate error bars.

    Parameters
    ----------
    data : array_like
        input data array

    Returns
    -------
    errbars : ndarray
        data array

    """
    errbars = np.zeros_like(data)
    return errbars


def line_eval(p, x):
    """Evaluate equation of line for each x.

    Parameters
    ----------
    p : tuple
        two-tuple line equation parameters (m=slope, b=y-intercept)
    x : float
        x value

    Returns
    -------
    y : float
        Evaluates equation of a line at point x

    """
    return p[0] * x + p[1]


def line_fit_residuals(p, x, y):
    """Compute residuals of line fit.

    Parameters
    ----------
    p : array_like
        1-D array of fit parameters: array([m=slope, b=y-intercept])
    x : array_like
        x data
    y : array_like
        y data

    Returns
    -------
    ndarray
        difference in y data array and the array containing the
        equation of the line evaluated with the given fit parameters
        at each x.

    """
    return y - line_eval(p, x)


def normalize(data):
    """Normalize data.

    Parameters
    ----------
    data : array_like
        input data

    Returns
    -------
    data : ndarray
        normalized data

    """
    data = np.asarray(data)
    return data / np.amax(data)


def reblock_data(data):
    """Re-block data set.

    Parameters
    ----------
    data : array_like
        data array

    Returns
    -------
    data : ndarray
        re-blocked data array

    """
    pass


def smooth_data(data, xcol=0, ycol=1, w=None, xb=None, xe=None,
                npts=50, k=3, task=0, s=None, t=None, full_output=0, per=0,
                quiet=1):
    """Smooth 1-D curve using B-spline.

    Parameters
    ----------
    data : array_like
        The data set defining a curve y = f(x).
    xcol, ycol : int
        The x and y data axes.
    w : array_like
        Strictly positive rank-1 array of weights the same length as x and
        y. The weights are used in computing the weighted least-squares
        spline fit. If the erros in the y values have standard-deviation
        given by the vector d, then w should be 1/d.
        Default is ones(len(x)).
    xb, xe: float
        The min, max bounds of interval to fit. If None, these
        default to x[0], x[-1], respectively.
    npts : int, optional
        The number of points between bounds.
    k : int, optional
        The order of the spline fit. It is recommended to use cubic
        splines.
    task : {1, 0, -1}, optional
        If task=0 find t and c for a given smoothing factor, s.
    s : float, optional
    t : int, optional
    full_output : bool, optional
    per : bool, optional
    quiet : bool, optional

    Returns
    -------
    data : ndarray
        smoothed data array

    """
    from scipy.interpolate import splrep, splev

    #r = linspace(r_min, r_max, r_step)
    #data = resize_array(data, r.min(), r.max())
    x = data[:, xcol]
    if xb is not None:
        x_min = xb
    else:
        x_min = x[0]
    if xe is not None:
        x_max = xe
    else:
        x_max = x[-1]

    y = resize_array(data, x_min, x_max)[:, ycol]
    tck = splrep(x, y)
    x_spline = np.linspace(x_min, x_max, npts)
    y_spline = splev(x_spline, tck, der=0)
    data = np.transpose((x_spline, y_spline))
    return data
