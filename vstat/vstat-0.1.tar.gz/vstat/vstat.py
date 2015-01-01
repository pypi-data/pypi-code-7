from __future__ import division

import scipy.special as sp
from math import sqrt, acos, sin, cos, pi


def vstat(n, p, Rsq):
    Rsq = .0001 if Rsq <= 0 else Rsq

    r = ((p - 1) * (1 - Rsq)) / ((n - p) * Rsq)
    g = min(r, 1)
    g = .5001 if 4999 < g < .5001 else g

    
    z = (g - sqrt(g - g**2)) / (2*g - 1)
    alpha = acos((1 - z) / sqrt(1 - 2*z * (1 - z)))

    v = (((2 * cos(alpha) * sp.gamma((p + 2) / 2)) /
        (sqrt(pi) * sp.gamma((p + 1) / 2))) *
        (sp.hyp2f1(.5, (1 - p) / 2, 3/2, cos(alpha)**2) -
        sin(alpha)**(p - 1)))

    return v
