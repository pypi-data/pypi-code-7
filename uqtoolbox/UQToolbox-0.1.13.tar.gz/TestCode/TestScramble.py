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


"""
Created on Mon Nov 26 22:43:30 2012

@author: dabi
"""

import numpy as np

from sobol_lib import scramble
from sobol_lib import sobol_generate
from sobol_lib import scrambled_sobol_generate

import matplotlib.pyplot as plt 

from scipy import stats

plt.close('all')

a = np.array([4, 3, 4, 2, 0, 1, 5])

aS = scramble(a)

# Try random seq, original sobol seq and scrambled one
N = 128
k = 2

ran = np.reshape( stats.uniform().rvs(size=k*N), (N,k) )
sobol = sobol_generate(k,N,2**np.ceil(np.log2(N)),0)
scramSobol = scrambled_sobol_generate(k,N,2**np.ceil(np.log2(N)),0)
scramSobol1 = scrambled_sobol_generate(k,N,2**(np.ceil(np.log2(N))+1),0)

plt.figure(figsize=(10,10))
plt.subplot(2,2,1)
plt.plot(ran[:,0],ran[:,1],'.')
plt.subplot(2,2,2)
plt.plot(sobol[:,0],sobol[:,1],'.')
plt.subplot(2,2,3)
plt.plot(scramSobol[:,0],scramSobol[:,1],'.')
plt.subplot(2,2,4)
plt.plot(scramSobol1[:,0],scramSobol1[:,1],'.')

plt.figure(figsize=(10,10))
plt.subplot(2,2,1)
H, xedges, yedges = np.histogram2d(ran[:,0], ran[:,1], bins=(10, 10),normed=True)
extent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
plt.imshow(H, extent=extent, interpolation='nearest')
plt.colorbar()
plt.show()
plt.subplot(2,2,2)
H, xedges, yedges = np.histogram2d(sobol[:,0], sobol[:,1], bins=(10, 10),normed=True)
extent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
plt.imshow(H, extent=extent, interpolation='nearest')
plt.colorbar()
plt.show()
plt.subplot(2,2,3)
H, xedges, yedges = np.histogram2d(scramSobol[:,0], scramSobol[:,1], bins=(10, 10),normed=True)
extent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
plt.imshow(H, extent=extent, interpolation='nearest')
plt.colorbar()
plt.show()
plt.subplot(2,2,4)
H, xedges, yedges = np.histogram2d(scramSobol1[:,0], scramSobol1[:,1], bins=(10, 10),normed=True)
extent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]
plt.imshow(H, extent=extent, interpolation='nearest')
plt.colorbar()
plt.show()

# Test quadrature properties
def f(X,s):
    if len(X.shape) == 1:
        return 12.**(s/2.) * np.prod( X - 0.5 )
    elif len(X.shape) == 2:
        return 12.**(s/2.) * np.prod( X - 0.5, 1)

s = 5;

NN = 10**np.arange(1,5);

meanMC = np.zeros(len(NN))
meanSobol = np.zeros(len(NN))
meanSSobol = np.zeros(len(NN))
varMC = np.zeros(len(NN))
varSobol = np.zeros(len(NN))
varSSobol = np.zeros(len(NN))
for (N,iNN) in zip(NN,range(0,len(NN))):
    XMC = np.reshape(stats.uniform.rvs(size=s*N),(N,s));
    meanMC[iNN] = 1./N * np.sum(f(XMC,s))
    varMC[iNN] = 1./N * np.sum(f(XMC,s) ** 2.) - meanMC[iNN]**2.
    
    XSobol = sobol_generate(s,N,2**np.ceil(np.log2(N)),0)
    meanSobol[iNN] = 1./(N) * np.sum(f(XSobol,s))
    varSobol[iNN] = 1./N * np.sum(f(XSobol,s) ** 2.) - meanSobol[iNN]**2.
    
    XSSobol = scrambled_sobol_generate(s,N,2**np.ceil(np.log2(N)),0)
    meanSSobol[iNN] = 1./(N) * np.sum(f(XSSobol,s))
    varSSobol[iNN] = 1./N * np.sum(f(XSSobol,s) ** 2.) - meanSSobol[iNN]**2.

plt.figure()
plt.loglog(NN,1./np.sqrt(NN),'r-')
plt.loglog(NN,NN**(-1.5),'r-')
plt.loglog(NN,abs(meanMC),'*-b')
plt.loglog(NN,abs(meanSobol),'*-k')
plt.loglog(NN,abs(meanSSobol),'*-m')

plt.figure()
plt.loglog(NN,1./np.sqrt(NN),'r-')
plt.loglog(NN,NN**(-1.5),'r-')
plt.loglog(NN,abs(varMC-1),'*-b')
plt.loglog(NN,abs(varSobol-1),'*-k')
plt.loglog(NN,abs(varSSobol-1),'*-m')
