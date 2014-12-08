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


import warnings
import sys
import marshal, types

import numpy as np

from numpy import linalg as npla

from scipy import linalg as scla

from SpectralToolbox import Spectral1D
from SpectralToolbox import SpectralND

class GaussianField:
    """
    Provided a Covariance function and discretization points, it generates the Gaussian fields.

    :param function C: Covariance function C(x1,x2)
    """

    C = None
    L = None
    
    serialize_list = ['x','L']
    marshall_list = ['C']
    
    def __init__(self, C):
        self.C = C

    def __getstate__(self):
        dd = dict( [ (tag, getattr( self, tag )) for tag in self.serialize_list ] )
        dd['C_code'] = marshal.dumps(self.C.func_code)
        return dd
        
    def __setstate__(self, state):
        for tag in state.keys():
            if tag == 'C_code':
                code =  marshal.loads( state[tag] )
                self.C = types.FunctionType(code, globals(), "C")
            else:
                setattr(self, tag, state[tag])

    def fit(self, x):
        """
        Given some discretization points, it finds the Cholesky factorization to be used for the
        simulation of the random field
        
        :param np.ndarray x: array containing the discretization points
        """
        self.x = x
        X1,X2 = np.meshgrid(x,x)
        self.L = npla.cholesky( self.C(X1,X2) )
        self.nvars = len(self.x)
    
    def transform(self, xi):
        """
        Generates random fields from the input variables (Normally distributed)
        
        :param np.ndarray xi: 1 or 2 dimensional array containing the generating variables. If 2-dimensional, each row should contain a different sample.
        
        :returns: the realizations of the random field
        :rtype: np.ndarray
        """
        if xi.ndim == 1:
            xi = np.array([xi])
        return np.dot( self.L, xi.T ).T
        

class KLExpansion:
    """
    KLExpansion: Computes the 1D KL expansion of the covariance matrix C, using the Legendre-Gauss-Loabatto rule for the solution to the generalized eigenvalue problem A * u = lmb * M * u.
    The KLExpansion of d-dimensional random fields is obtained by tensor product.

    :param function C: Covariance function C(x1,x2)
    :param int d: dimension of the tensorized field
    :param list spans: list of tuples containing the spans spans of the coordinates of the domain of C(x1,x2)
    """

    C = None
    N = None
    d = None
    spans = None
    targetVar = None
    totVar = None
    
    x = None
    w = None
    eigvals = None
    eigvecs = None
    nvars = None
    tensor_valI = None
    order_valI = None

    # New points on which to interpolate the eigenvalues
    # These are auxiliary in order to speed up the computations
    xs_fit = None
    eigvecs_fit = None 
    multidim_eigvecsvals = None

    serialize_list = ['N','d','targetVar','totVar','x','w','eigvals','eigvecs','nvars','tensor_valI','order_valI','spans','xs_fit','eigvecs_fit','multidim_eigvecsvals']
    marshall_list = ['C']

    def __init__(self,C,d,spans):
        if isinstance(C,list):
            if len(C) == d:
                self.C = C
            else: raise TypeError("The length of C is not consistent with d")
        else:
            self.C = [C]*d
        self.d = d
        self.spans = spans

    def __getstate__(self):
        dd = dict( [ (tag, getattr( self, tag )) for tag in self.serialize_list ] )
        dd['C_code'] = [marshal.dumps(C.func_code) for C in self.C]
        return dd
        
    def __setstate__(self, state):
        for tag in state.keys():
            if tag == 'C_code':
                self.C = []
                if isinstance(state[tag],list):
                    # For new format with anisotropic covariances
                    for C_code in state[tag]:
                        code =  marshal.loads( C_code )
                        self.C.append(types.FunctionType(code, globals(), "C"))
                else:
                    code =  marshal.loads( state[tag] )
                    self.C.append(types.FunctionType(code, globals(), "C"))
            else:
                setattr(self, tag, state[tag])
    
    def scale(self,i,x):
        """ Scales values x in [-1,1] to ``self.spans[i]``.
        """
        return ((x+1.)/2. + self.spans[i][0]) * (self.spans[i][1] - self.spans[i][0])
    
    def invscale(self,i,x):
        """ Scales values x in ``self.spans[i]`` to [-1,1].
        """
        return (x-self.spans[i][0])/(self.spans[i][1]-self.spans[i][0]) * 2. - 1.

    def fit(self,N,targetVar=.95):
        """
        Sets up the KL-expansion eigenvalues and eigenvectors for the required tolerance.

        :param list N: list of number of discretization points per dimension
        :param float targetVar: total variance to be represented by the output KL-expansion
        """
        self.N = N
        self.targetVar = targetVar
        
        self.x = []
        self.w = []

        self.eigvals = []
        self.eigvecs = []
        
        for d in xrange(self.d):
            # Lagrange polynomials....
            poly = Spectral1D.Poly1D(Spectral1D.JACOBI,[0.,0.])
            (xI,wI) = poly.GaussLobattoQuadrature(2 * self.N[d])
            wI /= np.sum(wI)
            self.x.append(xI)
            self.w.append(wI)

            xSc = self.scale(d,xI)
            X1,X2 = np.meshgrid(xSc,xSc)

            M = np.diag(wI)
            K = np.dot(M, np.dot(self.C[d](X1,X2),M ) )

            ''' Solve generalized eigenvalue problem '''
            (valI,vecI) = scla.eigh(K,M)
            # Normalize vectors and transfer normalization constant to eigenvalues
            nrm = np.diag( np.dot( np.multiply( wI, vecI.T ) , vecI ))
            vecI = np.multiply( 1./nrm , vecI )
            valI *= nrm
            # Sort in ascending order
            order = valI.argsort()[::-1]
            valI = valI[order]
            vecI = vecI[:,order]
            # Truncate to N
            valI = np.real(valI[:self.N[d]])
            vecI = np.real(vecI[:,:self.N[d]])

            TOTVAR = np.sum( valI )
            if TOTVAR > 1. + 1e-10:
                warnings.warn("UQToolbox.ModelReduction.KLExpansion: The total variance expressed by the KL-expansion exceed 1. TOTVAR = %f" % TOTVAR ,RuntimeWarning)
            
            self.eigvals.append(valI)
            self.eigvecs.append(vecI)

        tensor_valI = reduce(np.multiply, np.ix_( *self.eigvals ))
        order_valI = np.vstack(np.unravel_index(np.argsort(tensor_valI,axis=None)[::-1],(tensor_valI.shape) ))
        self.tensor_valI = tensor_valI
        self.order_valI = order_valI

        ''' Compute variance represented by the successive modes '''
        j = 0
        self.totVar = 0.
        while (self.totVar < self.targetVar) and (j < order_valI.shape[1]):
            tmp = 1.
            for i in range(self.d):
                tmp *= self.eigvals[i][order_valI[i,j]] * \
                    np.dot( wI * self.eigvecs[i][:,order_valI[i,j]], self.eigvecs[i][:,order_valI[i,j]])
            self.totVar += tmp
            j += 1

        if self.totVar < self.targetVar:
            warnings.warn("UQToolbox.ModelReduction.KLExpansion: length of the expansion not sufficient to resolve the target variance:\n KL-expansion: Target Variance      = %f \n KL-expansion: Represented Variance = %f" % (self.targetVar, self.totVar), RuntimeWarning)
        
        self.nvars = j        
    
    def fit_grid(self, xs):
        """ Used to pre-fit the eigenfunctions to a set of grid points.
        :params list xs: list of d coordinates for each direction
        """

        shape = tuple([len(x) for x in xs])
        # Scale the values to the interval [-1,1]
        self.xs_fit = [ self.invscale(i,x) for i,x in enumerate(xs) ]

        # Extrapolate values of eigenvalues at points x
        self.eigvecs_fit = []
        for j in xrange(self.d):
            if len(self.x[j]) == len(self.xs_fit[j]) \
               and npla.norm( self.x[j] - self.xs_fit[j] ) <= np.spacing(1):
                self.eigvecs_fit.append( self.eigvecs[j] )
            else:
                self.eigvecs_fit.append( Spectral1D.LagrangeInterpolate(self.x[j], self.eigvecs[j], self.xs_fit[j]) )
    
        self.multidim_eigvecsvals = []
        for j in xrange(self.nvars):
            tmp = np.ones(1)
            for i in range(self.d):
                tmp = np.kron(tmp, np.sqrt(self.eigvals[i][self.order_valI[i,j]]) * self.eigvecs_fit[i][:,self.order_valI[i,j]] )
            self.multidim_eigvecsvals.append(tmp)
        self.multidim_eigvecsvals = np.array(self.multidim_eigvecsvals).T

    def transform(self,xs,xi):
        """
        :params list xs: list of d coordinates for each direction
        :params list xi: list of 1 dimensional arrays of ``self.nvars`` values xi
        """
        
        shape = tuple([len(x) for x in xs])
        # Scale the values to the interval [-1,1]
        xs = [ self.invscale(i,x) for i,x in enumerate(xs) ]

        NR = len(xi)

        if np.any( [len(x) for x in xi] != [self.nvars]*NR ):
            raise RuntimeError("UQToolbox.ModelReduction.KLExpansion: the number of coefficients is not consistent with the length of the expansion.")

        # Extrapolate values of eigenvalues at points x
        eigvecs = []
        PREFIT = False
        for j in xrange(self.d):
            if len(self.x[j]) == len(xs[j]) and npla.norm( self.x[j] - xs[j] ) <= np.spacing(1):
                eigvecs.append( self.eigvecs[j] )
            elif self.xs_fit != None and len(self.xs_fit[j]) == len(xs[j]) and npla.norm( self.xs_fit[j] - xs[j] ) <= np.spacing(1):
                PREFIT = True
            else:
                eigvecs.append( Spectral1D.LagrangeInterpolate(self.x[j], self.eigvecs[j], xs[j]) )
        
        # Compute the KL-expansion for xi at the self.x points (Pascal's triangle)
        if PREFIT:
            u = [ np.dot( self.multidim_eigvecsvals, xi[i] ) for i in xrange(NR) ]
        else:
            u = [ 0. for i in xrange(NR) ]
            for j in xrange(self.nvars):
                tmp = np.ones(1)
                for i in range(self.d):
                    tmp = np.kron(tmp, np.sqrt(self.eigvals[i][self.order_valI[i,j]]) * eigvecs[i][:,self.order_valI[i,j]] )
                for i in xrange(NR):
                    u[i] += tmp * xi[i][j]
        
        for i in xrange(NR): u[i] = np.reshape(u[i],shape)
        return u

def KLExpansion1D(C,N,span,targetVar=0.95):
    """
    :note: Deprecated. Use the class ``KLExpansion`` instead

    KLExpansion: Computes the 1D KL expansion of the covariance matrix C, using the
       Legendre-Gauss-Loabatto rule for the solution to the generalized eigenvalue 
       problem A * u = lmb * M * u

    :param function C: Covariance function C(x1,x2)
    :param int N: number of discretization points    
    :param tuple span: span of the domain of C(x1,x2)
    :param float targetVar: total variance to be represented by the output KL-expansion    
    """
    warnings.warn("UQToolbox.ModelReduction.KLExpansion1D: This function is deprecated. Use the UQToolbox.ModelReduction.KLExpansion class instead.", DeprecationWarning)
    
    KLE = KLExpansion(C,1,[span])
    KLE.fit([N],targetVar)
    return (KLE.x, KLE.eigvals, KLE.eigvecs, KLE.totVar, KLE.nvars)
