"""
=======================================================================
Functions for transforms (:mod:`pksci.tools._transforms`)
=======================================================================

.. currentmodule:: pksci.tools._transforms

"""
from __future__ import division, print_function, absolute_import

import numpy as np
from numpy import cos, sin

__all__ = ['rotation_matrix']


def rotation_matrix(angle, rot_axis='z', deg2rad=False):
    """Generate a rotation matrix.

    Parameters
    ----------
    angle : float
        rotation angle in radians
    rot_axis : {'x', 'y', 'z'}, optional
        .. versionchanged:: 0.3.9
           Changed `axis` to `rot_axis` to prevent conflicts with numpy axis.
        rotation axis
    deg2rad : bool, optional
        .. versionadded:: 0.3.9
        Angle is in degrees and needs to be converted to radians

    Returns
    -------
    ndarray
        rotation matrix

    """
    if deg2rad:
        angle = np.radians(angle)
    if rot_axis == 'x':
        return np.array([[1, 0, 0],
                         [0, cos(angle), -sin(angle)],
                         [0, sin(angle), cos(angle)]])
    elif rot_axis == 'y':
        return np.array([[cos(angle), 0, sin(angle)],
                         [0, 1, 0],
                         [-sin(angle), 0, cos(angle)]])
    else:
        return np.array([[cos(angle), -sin(angle), 0],
                         [sin(angle), cos(angle), 0],
                         [0, 0, 1]])
