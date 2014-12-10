"""
General purpose shared mathematics routines
"""

import math


# @see: http://svn.gna.org/svn/relax/1.3/maths_fns/coord_transform.py
def spherical_to_cartesian(distance, azm, inc):
    sin_theta = math.sin(inc)
    x = distance * math.cos(azm) * sin_theta
    y = distance * math.sin(azm) * sin_theta
    z = distance * math.cos(inc)
    return x, y, z
