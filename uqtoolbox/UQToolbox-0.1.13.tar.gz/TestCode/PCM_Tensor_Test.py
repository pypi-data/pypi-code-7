# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 10:03:52 2012

@author: dabi
"""

from numpy import *
from scipy import stats
from matplotlib.pyplot import *

import Spectral1D as spec1D
import UncertaintyQuantification

close('all')

#dists = [stats.uniform(), stats.norm(0,1), stats.norm(2,3), stats.norm(2,3), stats.norm(2,3)]
#polys = [spec1D.Poly1D(spec1D.JACOBI,(0,0)), spec1D.Poly1D(spec1D.HERMITEP_PROB,None), spec1D.Poly1D(spec1D.HERMITEP_PROB,None), spec1D.Poly1D(spec1D.HERMITEP_PROB,None), spec1D.Poly1D(spec1D.HERMITEP_PROB,None)]
#distsPoly = [stats.uniform(), stats.norm(0,1), stats.norm(0,1), stats.norm(0,1), stats.norm(0,1)]
#Ns = [3,3,4,5,10]

#dists = [stats.uniform(), stats.norm(2,1)]
#polys = [spec1D.Poly1D(spec1D.JACOBI,(0,0)), spec1D.Poly1D(spec1D.HERMITEP_PROB,None)]
#distsPoly = [stats.uniform(-1,2), stats.norm(0,1)]
#Ns = [8,10]

dists = [stats.norm(-3,4), stats.norm(2,1)]
polys = [spec1D.Poly1D(spec1D.HERMITEP_PROB,None), spec1D.Poly1D(spec1D.HERMITEP_PROB,None)]
distsPoly = [stats.norm(0,1), stats.norm(0,1)]
Ns = [3,2]

dictionary = UncertaintyQuantification.PCM_Tensor(dists,polys,distsPoly,Ns,True)

vals = asarray(dictionary['vals'])
w = dictionary['wCub']
wPrj = dictionary['wPrj']
V = dictionary['V']

# Plot collocation points
figure()
plot(vals[:,0],vals[:,1],'.')