# -*- coding: utf-8 -*-

#
# This file is part of UQToolbox.
#
# UQToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UQToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with UQToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

import sys
import numpy as np

def MetropolisHastingsWithinGibbs(n, nMC, X0, target, propRG, propPDF):
    # n is the length of the Markov Chains
    # nMC is the number of Markov Chains (n. of samples)
    # target is the target function returning the log-likelihood
    # propRG is the random number generator for the proposed distribution
    # propPDF is the PDF of the proposed distribution
    from numpy.random import binomial as rbinom
    X = np.empty((n,nMC),dtype=np.float)
    X[0,:] = X0
    for t in range(0,n-1):
        XBase = X[t,:]
        for i in range(0,nMC):
            XNew = XBase.copy()
            XNew[i] = propRG(XBase[i],1)
            logR = ( target(XNew) + propPDF(XNew[i],XBase[i]) ) - ( target(XBase) + propPDF(XBase[i],XNew[i]))
            if logR > 0 :
                X[t+1,i] = XNew[i]
            else:
                # Random acceptance of step
                if rbinom(n=1,p=np.min((1,np.exp(logR))),size=1)[0]:
                    X[t+1,i] = XNew[i]
                else:
                    X[t+1,i] = X[t,i]
            if i < nMC:
                XBase = np.hstack( (X[t+1,:i+1] , X[t,i+1:]) )
    return X

def MetropolisHastings(n, nMC, X0, target, propRG, propPDF):
    # n is the length of the Markov Chains
    # nMC is the number of Markov Chains (n. of samples)
    # target is the target function returning the log-likelihood
    # propRG is the random number generator for the proposed distribution
    # propPDF is the PDF of the proposed distribution
    from numpy.random import binomial as rbinom
    X = np.empty((n,nMC),dtype=np.float)
    X[0,:] = X0
    for t in range(0,n-1):
        sys.stderr.write("MH Iteration: %d/%d\r" % (t,n))
        sys.stderr.flush()
        XBase = X[t,:]
        XNew = np.array([propRG(XBase[0],1)[0],propRG(XBase[1],1)[0]])
        logR = ( target(XNew) + propPDF(XNew[0],XBase[0]) + propPDF(XNew[1],XBase[1]) ) - ( target(XBase) + propPDF(XBase[0],XNew[0]) + propPDF(XBase[1],XNew[1]))
        if logR > 0 :
            X[t+1,:] = XNew
        else:
            # Random acceptance of step
            if rbinom(n=1,p=np.min((1,np.exp(logR))),size=1)[0]:
                X[t+1,:] = XNew
            else:
                X[t+1,:] = X[t,:]
    sys.stderr.write("\t")
    sys.stderr.flush()
    return X
