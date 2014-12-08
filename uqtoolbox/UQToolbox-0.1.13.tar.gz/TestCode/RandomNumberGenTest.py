# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 16:44:13 2012

@author: dabi
"""

from scipy import stats

from _UQToolbox import UncertaintyQuantification as UQ
from _UQToolbox import sobol_lib

N = 100
D = 2
RR = rand(N,D)
RS = sobol_lib.i4_sobol_generate(D,N,6)

figure(figsize=(10,5))
subplot(1,2,1)
plot(RR[:,0],RR[:,1],'.')
subplot(1,2,2)
plot(RS[0,:],RS[1,:],'.')

rsn = stats.beta(10,7).ppf(RS[0,:]);
figure()
hist(rsn,bins=40)