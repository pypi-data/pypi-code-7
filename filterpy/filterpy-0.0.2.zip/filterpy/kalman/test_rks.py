# -*- coding: utf-8 -*-
"""Copyright 2014 Roger R Labbe Jr.

filterpy library.
http://github.com/rlabbe/filterpy

This is licensed under an MIT license. See the readme.MD file
for more information.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
from filterpy.kalman import KalmanFilter, rks_smoother


if __name__ == '__main__':

    fk = KalmanFilter(dim_x=2, dim_z=1)

    fk.X = np.array([[-1.],
                    [1.]])         # initial state (location and velocity)

    fk.F = np.array([[1.,1.],
                     [0.,1.]])      # state transition matrix

    fk.H = [[1.,0.]]               # Measurement function
    fk.P = .01                     # covariance matrix
    fk.R = 5                       # state uncertainty
    fk.Q = 0.001                   # process uncertainty


    zs = [t + random.randn()*4 for t in range (40)]

    mu, cov,_,_ = fk.batch_filter (zs)
    mus = [x[0,0] for x in mu]

    M,P,C = rks_smoother(mu, cov, fk.F, fk.Q)



    # plot data
    p1, = plt.plot(zs,'cyan', alpha=0.5)
    p2, = plt.plot (M[:,0],c='b')
    p3, = plt.plot (mus,c='r')
    p4, = plt.plot ([0,len(zs)],[0,len(zs)], 'g') # perfect result
    plt.legend([p1,p2, p3, p4],
               ["measurement", "RKS", "KF output", "ideal"], 4)


    plt.show()

