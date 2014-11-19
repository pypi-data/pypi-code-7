# -*- coding: utf-8 -*-
"""Copyright 2014 Roger R Labbe Jr.

filterpy library.
http://github.com/rlabbe/filterpy

This is licensed under an MIT license. See the readme.MD file
for more information.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


from filterpy.kalman import ExtendedKalmanFilter


rf = ExtendedKalmanFilter(dim_x=3, dim_z=1)

