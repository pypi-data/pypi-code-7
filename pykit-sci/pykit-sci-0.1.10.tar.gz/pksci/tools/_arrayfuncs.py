"""
========================================================================
Functions for data arrays (:mod:`pksci.tools._arrayfuncs`)
========================================================================

.. currentmodule:: pksci.tools._arrayfuncs

"""
from __future__ import division, print_function, absolute_import

import numpy as np

__all__ = ['array_limits', 'array_range', 'resize_array', 'resize_matrix']


def array_limits(data, at_endpoints=False):
    """Compute limits of data array.

    Default is to find the min, max limits of data values.
    if `at_endpoints` is True, then return the first and last
    elements of the data array.

    Parameters
    ----------
    data : array_like
        input data
    at_endpoints : bool, optional
        return the first and last array elements

    Returns
    -------
    tuple
        default behavior will return (data.min(), data.max()).
        if at_endpoints=True then return (data[0], data[-1]).

    """
    data = np.asarray(data)

    if at_endpoints:
        return (data[0], data[-1])
    else:
        return (np.amin(data), np.amax(data))


def array_range(data, at_endpoints=False):
    """Compute range of data.

    Parameters
    ----------
    data : array_like
        input data
    at_endpoints : bool, optional

    Returns
    -------
    float
        range of data

    """
    data = np.asarray(data)

    if at_endpoints:
        return data[-1] - data[0]
    else:
        return np.amax(data) - np.amin(data)


def resize_array(A, min_, max_, col=0):
    """Resize an array.

    Parameters
    ----------
    A : array_like
        Input data.
    min_ : {int, float}
        minimum value of data allowed in returned array slice
    max_ : {int, float}
        maximum value of data allowed in returned array slice
    col : int
        corresponding col for min/max slicing (default=0)

    Returns
    -------
    A : ndarray
        resized array

    """
    A = np.asarray(A)
    A = A[A[:, col] >= min_, :]
    A = A[A[:, col] <= max_, :]

    return A


def resize_matrix(M, min_, max_, col=0):
    """Resize a matrix.

    Parameters
    ----------
    M : array_like
        Input data.
    min_ : {int, float}
        minimum value of data allowed in returned matrix slice
    max_ : {int, float}
        maximum value of data allowed in returned matrix slice
    col : int
        corresponding col for min/max slicing (default=0)

    Returns
    -------
    M : matrix
        resized matrix.

    """
    M = np.asmatrix(M)

    M = M[M.A[:, col] >= min_, :]
    M = M[M.A[:, col] <= max_, :]

    return M
