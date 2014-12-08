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

import numpy as np

from numpy import linalg as la

from scipy import stats

import itertools

from prettytable import PrettyTable

from SpectralToolbox import Spectral1D
from SpectralToolbox import SpectralND
from SpectralToolbox import SparseGrids

def gPC_MultiIndex(dist,poly,distPoly,N,NI=[],quadTypes=None,left=None,right=None,end=None,warnings=True):
    """
    gPC_MultiIndex(dist,poly,distPoly,N)
    Generates the Multi Index basis Vandermonde matrix using the list of 
    distributions of the parameters space approximated by the selected polynomials.

    :param dist: list of n distributions representing the n-Dimensional random space
    :param poly: list of n polynomials (class Spectral1D) used for approximating each of the directions in the random space
    :param distPoly: list of n standard distributions associated to the polynomial selected
    :param N: maximum polynomial order in the basis
    :param NI: (int) number of points in which to evaluate the basis functions for precise cubature rules (if NI=[], the interpolated vandermonde is not evaluated)
    :param quadTypes: (list, ``Spectral1D.AVAIL_POINTS``) list of n types of quadrature points among Gauss, Gauss-Lobatto and Gauss-Radau. If ``None``, Gauss quadrature points are used.
    :param left: (list,float) list of left values used by ORTHPOL for Gauss-Lobatto rules (the dimensions where the value is not used can be set to anything)
    :param right: (list,float) list of left values used by ORTHPOL for Gauss-Lobatto rules (the dimensions where the value is not used can be set to anything)
    :param end: (list,float) list of left values used by ORTHPOL for Gauss-Radau rules (the dimensions where the value is not used can be set to anything)
    :param warnings: True if you want to read warning on memory allocation
    
    :returns: dictionary with the following attributes
        ``x``: tensor product of collocation points in the standard distributions
        ``w``: tensor product of the weights for cubature/projection rules (sum to 1 or prod(gamma0) respectively)
        ``vals``: tensor product of collocation points
        ``V``: Pascal's simplex of the basis functions
    """
    
    if (len(dist) != len(distPoly) or len(distPoly) != len(poly)) :
        print "The number of elements in dist, distPoly and poly is not consistent"
        return
    else:
        DIM = len(dist)

    if quadTypes == None:
        quadTypes = [Spectral1D.GAUSS for i in range(DIM)]
    if left == None:
        left = [None for i in range(DIM)]
    if right == None:
        right = [None for i in range(DIM)]
    if end == None:
        end = [None for i in range(DIM)]

    if DIM != len(quadTypes) or DIM != len(left) or DIM != len(right) or DIM != len(end):
        print "The number of elements in quadTypes, left, right, end are not consistent"
        return

    pp = SpectralND.PolyND(poly)
    
    (x, w) = pp.Quadrature(np.tile(N,DIM),quadTypes=quadTypes,normed=False, left=left, right=right, end=end)
    
    # Compute relative samples using inverse CDF method
    vals = np.zeros(np.asarray(x).shape)
    for i in range(0,DIM):
        vals[:,i] = dist[i].ppf(distPoly[i].cdf(x[:,i]))
    
    # Compute Generalized Vandermonde if required
    xs = []
    for i in range(0,DIM):
        x1D, _ = poly[i].Quadrature(N,quadType=quadTypes[i],normed=False,left=left[i], right=right[i], end=end[i])
        xs.append(x1D)
    V = pp.GradVandermondePascalSimplex(xs, N, np.zeros(DIM,dtype=int), norms=None, warnings=warnings)
    
    # Compute interpolated values of the Vandermonde matrix
    (xI, wI) = pp.Quadrature(np.tile(NI,DIM),quadTypes=quadTypes,normed=False, left=left, right=right, end=end)
    
    xs = []
    for i in range(0,DIM):
        x1D, _ = poly[i].Quadrature(NI,quadType=quadTypes[i],normed=False,left=left[i], right=right[i], end=end[i])
        xs.append(x1D)
    VI = pp.GradVandermondePascalSimplex(xs, N, np.zeros(DIM,dtype=int), norms=None)

    IDX = SpectralND.MultiIndex(DIM,N)
    
    # Create Dictionary
    dictionary = {'x':    x,
                  'w':    w,
                  'vals': vals,
                  'V':    V,
                  'xI':   xI,
                  'wI':   wI,
                  'VI':   VI,
                  'IDX':  IDX}
    
    return dictionary

def PCM_Tensor(dist,poly,distPoly,Ns,allocBasis=True):
    """
    PCM_Tensor(dist,poly,distPoly,N)
    Generates the full tensor grid using the list of distributions of the parameters
    space approximated by the selected polynomials.

    :param dist: list of n distributions representing the n-Dimensional random space
    :param poly: list of n polynomials (class Spectral1D) used for approximating each of the directions in the random space
    :param distPoly: list of n standard distributions associated to the polynomial selected
    :param Ns: list of n integers for the order of polynomial expansion in each direction
    :param allocBasis: boolean. True if you want the tensor basis.
    
    :returns: dictionary with the following attributes
        'x': tensor product of collocation points in the standard distributions
        'w': tensor product of the weights for cubature/projection rules (sum to 1 or prod(gamma0) respectively)
        'vals': tensor product of collocation points
        'V': tensor basis functions
    """
    
    if (len(dist) != len(distPoly) or len(distPoly) != len(poly) or len(poly) != len(Ns)) :
        print "The number of elements in dist, distPoly and poly is not consistent"
        return
    else:
        DIM = len(dist)

    pp = SpectralND.PolyND(poly)
    
    if allocBasis:
        (x, w) = pp.GaussQuadrature(Ns,normed=False)
    else:
        (x, w) = pp.GaussQuadrature(Ns,normed=True)
    
    # Compute relative samples using inverse CDF method
    vals = np.zeros(np.asarray(x).shape)
    for i in range(0,DIM):
        vals[:,i] = dist[i].ppf(distPoly[i].cdf(x[:,i]))
    
    # Compute Generalized Vandermonde if required
    if allocBasis:
        xs = []
        for i in range(0,DIM):
            x1D, w1D = poly[i].GaussQuadrature(Ns[i])
            xs.append(x1D)
        V = pp.GradVandermonde(xs, Ns, np.zeros(DIM,dtype=int), None)
    
    # Create Dictionary
    if allocBasis:
        dictionary = {'x': x,
                      'w': w,
                      'vals': vals,
                      'V': V}
    else:
        dictionary = {'x': x,
                      'w': w,
                      'vals': vals}
    return dictionary

def UQ_PCM_Tensor(solve,params,solvePostProcessing,dists,paramUpdate,polys,distsPoly,Ns,method):
    """
    DESCRIPTION:
        UQ_PCM_Tensor(solve,params,solvePostProcessing,dists,paramUpdate,polys,distsPoly,N,method)
        Performs Uncertainty Quantification analysis of the system described by rhs using the Probabilistic Collocation Method by Tensor Product of the random space.
    INPUT:
        - solve: function handle to the experiment to be quantified. Signature: sol = solve(sample,params)
        - params: parameters to be passed to the ODE system (these contain the uncertain parameter as well)
        - solvePostProcessing: post processing function called after all the simulation have been run. Signature: sols = solvePostProcessing(sols)
        - dists: list of n scipy.stats distribution functions for each uncertain parameter
        - paramUpdate: function handle for updating the set of uncertain parameters. Signature: params = paramUpdate(params,sample)
        - polys: list of n Spectral1D polynomials using for approximating the distribution of the random parameters
        - distsPoly: list of n standard distributions associated to the selected approximating polynomials
        - Ns: list of n integers for the order of polynomial expansion in each random direction
        - method: 'projection' use projection rule in order to compute statistics, 'cubature' use cubature rule in order to compute statistics
    OUTPUT: dictionary with the following attributes
        - 'Samples': list of collocation points (samples) used for UQ
        - 'Y': solutions at collocation points
        - 'YHat': Galerkin coefficients (available only if method == 'projection')
        - 'meanSol': estimated mean
        - 'varSol': estimated variance
    """    

    from mpi4py import MPI
        
    comm = MPI.COMM_WORLD
    myrank = comm.Get_rank()
    
    if (len(dists) != len(distsPoly) or len(distsPoly) != len(polys) or len(polys) != len(Ns)) :
        print "The number of elements in dist, distPoly and poly is not consistent"
        return
    else:
        DIM = len(dists)

    if (method != 'projection') and (method != 'cubature'):
        print "The selected method '%s' does not exist." % (method)
        return
    
    ###################################################################################
    #                              PRE - PROCESSING                                   #
    ###################################################################################
    
    if method == 'projection':
        dictionary = PCM_Tensor(dists,polys,distsPoly,Ns,allocBasis=True)
        V = dictionary['V']
    if method == 'cubature':
        dictionary = PCM_Tensor(dists,polys,distsPoly,Ns,allocBasis=False)
    w = dictionary['w']
    vals = dictionary['vals']
    Ncoll = len(vals)
    
    ###################################################################################
    #                              SIMULATION                                         #
    ###################################################################################
        
    def action(sols,sol):
        sols.append(sol)
        return sols
        
    solutions = run_experiments(solve,vals,params,paramUpdate,action)
    
    if myrank == 0:
        solutions = solvePostProcessing(solutions)    
    
    ###################################################################################
    #                              POST-PROCESSING                                    #
    ###################################################################################
    
    if myrank == 0:
        # Reshape the solutions so that they are [Ncoll x NDOF], where NDOF is the total DOF
        # Example: for a time dep. ode NDOF = DOF x len(t)
        solsShape = solutions[0].shape
        NDOF = np.prod(solsShape)
        solsRS = np.zeros( (Ncoll, NDOF) )
        for i in range(0,Ncoll):
            # For each solution
            solsRS[i,:] = np.reshape(solutions[i],np.prod(solsShape))
        
        # Post processing for the computation of the PCM coefficients
        # using discrete projection
        def PCM_PostProcProjection(sols):
            # Compute gPC post processing on sols
            # with the following order: DOF, samples, sols
            solsHat = np.zeros(sols.shape)
            A = V * np.tile(w,(1,V.shape[1]))
            for i in range(0,NDOF):
                # For each NDOF
                solsHat[:,i] = np.dot(A.T,sols[:,i])
            return solsHat
        
        if method == 'projection':
            solsHatRS = PCM_PostProcProjection(solsRS)
            
            # Compute mean
            gamma = polys[0].Gamma(0)
            for i in range(1,DIM):
                gamma = gamma * polys[i].Gamma(0)
            meanSol = solsHatRS[0,:] / np.sqrt(gamma)
            
            # Compute variance
            varSol = np.zeros(NDOF)
            for i in range(0,NDOF):
                    varSol[i] = sum(solsHatRS[1:,i]**2.)
        
        if method == 'cubature':
            meanSol = np.zeros(NDOF)
            varSol = np.zeros(NDOF)
            
            for i in range(0,NDOF):
                meanSol[i] = np.dot(solsRS[:,i],w)
                varSol[i] = np.dot(solsRS[:,i]**2.,w) - meanSol[i]**2.
        
        # Reshape the solutions and the statistics to the original shapes
        sols = np.zeros((Ncoll,)+solsShape)
        for i in range(0,Ncoll):
            sols[i,:] = np.reshape(solsRS[i,:],solsShape)
        meanSol = np.reshape(meanSol,solsShape)
        varSol = np.reshape(varSol,solsShape)
        if method == 'projection':
            solsHat = np.zeros((Ncoll,)+solsShape)
            for i in range(0,Ncoll):
                solsHat[i,:] = np.reshape(solsHatRS[i,:],solsShape)
            
        ###################################################################################
        #                              OUTPUT                                             #
        ###################################################################################
        # Prepare a dictionary with necessary data
        if method == 'projection':
            dictionary = {'Samples': vals,
                          'Y': sols,
                          'YHat': solsHat,
                          'meanSol': meanSol,
                          'varSol': varSol}
        if method == 'cubature':
            dictionary = {'Samples': vals,
                          'Y': sols,
                          'meanSol': meanSol,
                          'varSol': varSol}
        return dictionary

def UQ_SparseGrid(solve,params,solvePostProcessing,dists,paramUpdate,method,k,sym=1):
    """
    DESCRIPTION:
        UQ_PCM_Tensor(solve,params,solvePostProcessing,dists,paramUpdate,polys,distsPoly,N,method)
        Performs Uncertainty Quantification analysis of the system described by rhs using the Probabilistic Collocation Method by Tensor Product of the random space.
    INPUT:
        - solve: function handle to the experiment to be quantified. Signature: sol = solve(sample,params)
        - params: parameters to be passed to the ODE system (these contain the uncertain parameter as well)
        - solvePostProcessing: post processing function called after all the simulation have been run. Signature: sols = solvePostProcessing(sols)
        - dists: list of n scipy.stats distribution functions for each uncertain parameter
        - paramUpdate: function handle for updating the set of uncertain parameters. Signature: params = paramUpdate(params,sample)
        - method: Sparse Grid method selected. See description below.
        - k: accuracy of the Sparse Grid rule
        - sym: [optional, default = 1] symmetry parameter for Sparse Grid package
    OUTPUT: dictionary with the following attributes
        - 'Samples': list of collocation points (samples) used for UQ
        - 'Y': solutions at collocation points
        - 'meanSol': estimated mean
        - 'varSol': estimated variance
    Description:
        The methods available for sparse grid are:
            * KPU = Nested rule for unweighted integral over [0,1]
            * KPN = Nested rule for integral with Gaussian weight
            * GQU = Gaussian quadrature for unweighted integral over [0,1] (Gauss-Legendre)
            * GQN = Gaussian quadrature for integral with Gaussian weight (Gauss-Hermite)
            * func =  any function provided by the user that accept level l and returns nodes n and weights w for univariate quadrature rule with polynomial exactness 2l-1 as [n w] = feval(func,level)
    """    

    from mpi4py import MPI
    
    comm = MPI.COMM_WORLD
    myrank = comm.Get_rank()
    
    DIM = len(dists)

    if (method != SparseGrids.KPU) and (method != SparseGrids.KPN) and (method != SparseGrids.GQU) and (method != SparseGrids.GQN) and (not callable(method)):
        print "The selected method '%s' does not exist." % (method)
        return
    
    ###################################################################################
    #                              PRE - PROCESSING                                   #
    ###################################################################################
    
    sg = SparseGrids.SparseGrid(method, DIM, k, sym);
    (n,w) = sg.sparseGrid();
    
    vals = n.copy();
    if (method == SparseGrids.KPN) or (method == SparseGrids.GQN):
        ndist = stats.norm(0.,1.);
        for i in range(0,DIM):
            vals[:,i] = dists[i].ppf(ndist.cdf(n[:,i]))
    elif (method == SparseGrids.KPU) or (method == SparseGrids.GQU):
        udist = stats.uniform(0.,1.);
        for i in range(0,DIM):
            vals[:,i] = dists[i].ppf(udist.cdf(n[:,i]))
    
    Ncoll = vals.shape[0]
    
    ###################################################################################
    #                              SIMULATION                                         #
    ###################################################################################
        
    def action(sols,sol):
        sols.append(sol)
        return sols
        
    solutions = run_experiments(solve,vals,params,paramUpdate,action)
    
    if myrank == 0:
        solutions = solvePostProcessing(solutions)    
    
    ###################################################################################
    #                              POST-PROCESSING                                    #
    ###################################################################################
    
    if myrank == 0:
        # Reshape the solutions so that they are [Ncoll x NDOF], where NDOF is the total DOF
        # Example: for a time dep. ode NDOF = DOF x len(t)
        solsShape = solutions[0].shape
        NDOF = np.prod(solsShape)
        solsRS = np.zeros( (Ncoll, NDOF) )
        for i in range(0,Ncoll):
            # For each solution
            solsRS[i,:] = np.reshape(solutions[i],np.prod(solsShape))
        
        if method == 'cubature':
            meanSol = np.zeros(NDOF)
            varSol = np.zeros(NDOF)
            
            for i in range(0,NDOF):
                meanSol[i] = np.dot(solsRS[:,i],w)
                varSol[i] = np.dot(solsRS[:,i]**2.,w) - meanSol[i]**2.
        
        # Reshape the solutions and the statistics to the original shapes
        sols = np.zeros((Ncoll,)+solsShape)
        for i in range(0,Ncoll):
            sols[i,:] = np.reshape(solsRS[i,:],solsShape)
        meanSol = np.reshape(meanSol,solsShape)
        varSol = np.reshape(varSol,solsShape)
            
        ###################################################################################
        #                              OUTPUT                                             #
        ###################################################################################
        # Prepare a dictionary with necessary data
        dictionary = {'Samples': vals,
                      'Y': sols,
                      'meanSol': meanSol,
                      'varSol': varSol}
        return dictionary

class MEPCM_Element:
    ###########
    # PARAMETERS CONSTRUCTED BY THE USER OR REFINEMENT PROCEDURE
    DIM = 0;
    dists = []; # Stores the distributions along the D dimensions
    distsCond = []; # Stores the distribution scalings along the D dimensions
    el = []; # Stores the element coordinates along the D dimensions
    Ns = []; # Stores the order along the D dimensions
    finite = False; # True = the element is finite in all the dimensions, False = the element is infinite in at least one dimension
    ###########
    # DIRTY PARAMETER
    dirty = True; # True = tensor grid needs to be generated, False = nothing needs to be done
    ###########
    # PARAMETERS CONSTRUCED BY THE TENSOR GRID GENERATOR
    # 1D Parameters
    poly1D = []; # Stores the polynomial parameters along the D dimensions
    x1D = []; # Stores the collocation points needed by the element (in the scaled element reference frame)
    vals1D = []; # Stores the collocation points needed by the element
    w1D = []; # Stores the weights corresponding to the collocation points
    pr1D = []; # Stores the probability of the element Pr(I_B_k = 1)
    dim1D = []; # Stores the 1D element size
    V1D = []; # Stores the Vandermonde matrix for the element
    finite1D = []; # True = the element is finite the dimension, False = the element is infinite the dimension
    # ND Parameters
    xEl = []; # Stores the collocation points needed by the element (in the scaled element reference frame)
    valsEl = []; # Stores the collocation points needed by the element
    wEl = []; # Stores the weights corresponding to the collocation points
    prEl = 0.0; # Stores the probability of the element Pr(I_B_k = 1)
    dimEl = 0.0; # Stores the N-D hyper-volume of the element
    VEl = []; # Stores the Vandermonde matrix for the element
    orderEl = []; # Stores the tuples containing the order combination for each basis function
    
    def __init__(self, el, dists, distsCond, Ns):
        if (len(el) != len(dists) or len(dists) != len(Ns) or len(Ns) != len(distsCond)) :
            print "The number of elements in rs, Ns, ks and norms is not consistent"
            return
        
        self.DIM = len(el);
        
        self.dists = dists;
        self.distsCond = distsCond;
        self.el = el;
        self.Ns = Ns;
        
        self.poly1D = []; # Stores the polynomial parameters along the D dimensions
        self.x1D = []; # Stores the collocation points needed by the element (in the scaled element reference frame)
        self.vals1D = []; # Stores the collocation points needed by the element
        self.w1D = []; # Stores the weights corresponding to the collocation points
        self.pr1D = []; # Stores the probability of the element Pr(I_B_k = 1)
        self.dim1D = []; # Stores the 1D element size
        self.V1D = []; # Stores the Vandermonde matrix for the element
        self.finite1D = []; # True = the element is finite the dimension, False = the element is infinite the dimension
        # ND Parameters
        self.xEl = []; # Stores the collocation points needed by the element (in the scaled element reference frame)
        self.valsEl = []; # Stores the collocation points needed by the element
        self.wEl = []; # Stores the weights corresponding to the collocation points
        self.prEl = 0.0; # Stores the probability of the element Pr(I_B_k = 1)
        self.dimEl = 0.0; # Stores the N-D hyper-volume of the element
        self.VEl = []; # Stores the Vandermonde matrix for the element
        self.orderEl = []; # Stores the tuples containing the order combination for each basis function
        
        self.prEl = 1.0;
        self.dimEl = 1.0;
        for eld,distd in zip(self.el,self.dists):
            # Compute the elements probability
            pr = distd.cdf(eld[1])-distd.cdf(eld[0]);
            d = eld[1]-eld[0];
            self.pr1D.append(pr);
            self.dim1D.append(d);
            self.prEl *= pr;
            self.dimEl *= d;
        
        # Check if finite element
        self.finite = True;
        for eld in self.el:
            self.finite1D.append(not any(abs(eld) == np.inf));
            self.finite = self.finite and not any(abs(eld) == np.inf);
        
        self.dirty = True;
    
    def __getstate__(self):
        # Store parameters for polynomials
        poly1D_params = []
        for pp in self.poly1D:
            # Empty space for the measure (it is reconstructed at __setstate__ time)
            params = list(pp.params)
            params[5] = None
            poly1D_params.append( params )
        
        return dict(DIM = self.DIM,
#                    dists = self.dists,
#                    distsCond = self.distsCond,
                    el = self.el,
                    Ns = self.Ns,
                    finite = self.finite,
                    dirty = self.dirty,
                    poly1D_params = poly1D_params,
                    x1D = self.x1D,
                    vals1D = self.vals1D,
                    w1D = self.w1D,
                    pr1D = self.pr1D,
                    dim1D = self.dim1D,
                    V1D = self.V1D,
                    finite1D = self.finite1D,
                    xEl = self.xEl,
                    valsEl = self.valsEl,
                    wEl = self.wEl,
                    prEl = self.prEl,
                    dimEl = self.dimEl,
                    VEl = self.VEl,
                    orderEl = self.orderEl);
    
#    def __reduce__(self):
#        return (MEPCM_Element, ([],[],[],[]), self.__getstate__());
    
    def __setstate__(self,state,dists=None,distsCond=None):
        ###########
        # PARAMETERS CONSTRUCTED BY THE USER OR REFINEMENT PROCEDURE
        self.DIM = state['DIM'];
#        self.dists = state['dists']; # Stores the distributions along the D dimensions
#        self.distsCond = state['distsCond']; # Stores the distribution scalings along the D dimensions
        self.el = state['el']; # Stores the element coordinates along the D dimensions
        self.Ns = state['Ns']; # Stores the order along the D dimensions
        self.dists = dists;
        self.distsCond = distsCond;
        self.finite = state['finite']; # True = the element is finite in all the dimensions, False = the element is infinite in at least one dimension
        ###########
        # DIRTY PARAMETER
        self.dirty = state['dirty']; # True = tensor grid needs to be generated, False = nothing needs to be done
        ###########
        # PARAMETERS CONSTRUCED BY THE TENSOR GRID GENERATOR
        # 1D Parameters
        self.poly1D = []
        for d,params in enumerate(state['poly1D_params']):
            # Restore measure function definition
            if (abs(self.el[d][0]) == np.inf) or (abs(self.el[d][1]) == np.inf):
                # No mapping to [-1,1]. TAILS ARE ASSUMED TO GET RAPIDLY TO 0
                def wf_cap(y,i):
                    return self.dists[d].pdf(self.distCond[d](y,-1))/self.prEl;
            else:
                def wf_cap(y,i):
                    centEl = (self.el[d][1] + self.el[d][0])/2.;
                    dimEl = (self.el[d][1]-self.el[d][0]);
                    return self.dists[d].pdf(y * dimEl/2. + centEl)/self.prEl * dimEl * 0.5**self.DIM;
            
            params[5] = wf_cap
            self.poly1D.append(Spectral1D.Poly1D(Spectral1D.ORTHPOL,params))
#        self.poly1D = state['poly1D']; # Stores the polynomial parameters along the D dimensions
        self.x1D = state['x1D']; # Stores the collocation points needed by the element (in the scaled element reference frame)
        self.vals1D = state['vals1D']; # Stores the collocation points needed by the element
        self.w1D = state['w1D']; # Stores the weights corresponding to the collocation points
        self.pr1D = state['pr1D']; # Stores the probability of the element Pr(I_B_k = 1)
        self.dim1D = state['dim1D']; # Stores the 1D element size
        self.V1D = state['V1D']; # Stores the Vandermonde matrix for the element
        self.finite1D = state['finite1D']; # True = the element is finite the dimension, False = the element is infinite the dimension
        # ND Parameters
        self.xEl = state['xEl']; # Stores the collocation points needed by the element (in the scaled element reference frame)
        self.valsEl = state['valsEl']; # Stores the collocation points needed by the element
        self.wEl = state['wEl']; # Stores the weights corresponding to the collocation points
        self.prEl = state['prEl']; # Stores the probability of the element Pr(I_B_k = 1)
        self.dimEl = state['dimEl']; # Stores the N-D hyper-volume of the element
        self.VEl = state['VEl']; # Stores the Vandermonde matrix for the element
        self.orderEl = state['orderEl']; # Stores the tuples containing the order combination for each basis function
    
    def __clear1D(self):
        self.poly1D = []; # Stores the polynomial parameters along the D dimensions
        self.x1D = []; # Stores the collocation points needed by the element (in the scaled element reference frame)
        self.vals1D = []; # Stores the collocation points needed by the element
        self.w1D = []; # Stores the weights corresponding to the collocation points
        self.V1D = []; # Stores the Vandermonde matrix for the element
    
    def __clearTensor(self):
        self.xEl = []; # Stores the collocation points needed by the element (in the scaled element reference frame)
        self.valsEl = []; # Stores the collocation points needed by the element
        self.wEl = []; # Stores the weights corresponding to the collocation points
        self.VEl = []; # Stores the Vandermonde matrix for the element
        self.orderEl = []; # Stores the tuples containing the order combination for each basis function
    
    def getstate(self):
        return self.__getstate__();
    
    def setstate(self,state,dists=None,distsCond=None):
        self.__setstate__(state,dists,distsCond);
    
    def __InitBasis1D(self, allocBasis=True):
        """
        Basis1D([allocBasis=True])
        Generates the 1D basis using the list of distributions of the parameters
        space approximated by properly construced orthogonal polynomials.
        INPUT:
            ``allocBasis``: boolean. True if you want the tensor basis.
        OUTPUT:
        """
        
        self.__clear1D();
        
        #############
        # Generate 1D basis for each dimension
        for d in range(0,self.DIM):
            dist = self.dists[d];
            N = self.Ns[d];
            eld = self.el[d];
            distCond = self.distsCond[d];
            
            # Scale the element using user provided function
            elSC = distCond(eld, 1);
            
            # Prepare the measure function
            if (abs(eld[0]) == np.inf) or (abs(eld[1]) == np.inf):
                # No mapping to [-1,1]. TAILS ARE ASSUMED TO GET RAPIDLY TO 0
                def wf_cap(y,i):
                    return dist.pdf(distCond(y,-1))/self.prEl;
            else:
                def wf_cap(y,i):
                    centEl = (eld[1] + eld[0])/2.;
                    dimEl = (eld[1]-eld[0]);
                    return dist.pdf(y * dimEl/2. + centEl)/self.prEl * dimEl * 0.5**self.DIM;
            
            # Generate basis and Gauss points
            ncapm = 500;
            mc = 1;
            mp = 0;
            xp = np.array([]);
            yp = np.array([]);

            irout = 0; # 1: Use sti internally, 0: Use lancz
            if (abs(elSC[0]) == np.inf) or (abs(elSC[1]) == np.inf):
                # Do not apply scaling (we assume tails decay!!)
                x = elSC;
                if (abs(elSC[0]) == np.inf): finl = False; 
                else: finl = True;
                if (abs(elSC[1]) == np.inf): finr = False; 
                else: finr = True;
            else:
                x = np.linspace(-1.,1.,mc+1);
                centEl = (elSC[1] + elSC[0])/2.;
                dimEl = (elSC[1]-elSC[0])/2.;
                finr = True;
                finl = True;
            endl = x[:-1];
            endr = x[1:];
            
            params = (ncapm, mc, mp, xp, yp, wf_cap, irout,finl,finr,endl,endr)
            P = Spectral1D.Poly1D(Spectral1D.ORTHPOL,params)
            
            self.poly1D.append(P)

            (xg,wg) = P.GaussQuadrature(N)
            wg /= np.sum(wg);
            
            if finl and finr:
                x = xg * dimEl + centEl;
                self.x1D.append(x);
            else:
                x = xg;
                self.x1D.append(x);
            self.w1D.append(wg);
            self.vals1D.append(distCond(x,-1));
            
            if allocBasis:
                VCap = self.Vandermonde1D(self.vals1D[-1],d);
                self.V1D.append(VCap);

    def __InitTensor(self, allocBasis=True):
        """
        Tensor([allocBasis=True])
        Generates the full tensor grid using the list of distributions of the parameters
        space approximated by properly construced orthogonal polynomials.
        INPUT:
            ``allocBasis``: boolean. True if you want the tensor basis.
        OUTPUT:
        """
        
        self.__clearTensor();
        
        #############
        # Generate ND basis
        xs = [];
        vals = [];
        ords = [];
        wKron = np.array([1]);
        if allocBasis:
            VKron = np.array([1]);
        for d in range(0,self.DIM):
            ords.append(range(0,self.Ns[d]))
            xs.append(self.x1D[d]);
            vals.append(self.vals1D[d]);
            wKron = np.kron(wKron, self.w1D[d]);
            if allocBasis:
                VKron = np.kron(VKron, self.V1D[d]);
        self.xEl = np.asarray(list(itertools.product(*xs)))
        self.valsEl = np.asarray(list(itertools.product(*vals)))
        self.orderEl = list(itertools.product(*ords))
        self.wEl = wKron;
        if allocBasis:
            self.VEl = VKron;
    
    def Vandermonde1D(self,x,d):
        if not self.finite1D[d]:
            # Map to the Scaled values
            xSC = self.distsCond[d](x,1);
        if self.finite1D[d]:
            # Scale to [-1,1] if dimension is finite
            centEl = (self.el[d][1] + self.el[d][0])/2.
            dimEl = (self.el[d][1] - self.el[d][0])/2.
            xSC = (x - centEl)/dimEl
        return self.poly1D[d].GradVandermonde1D(xSC,self.Ns[d],0,norm=False);
    
    def TensorVandermonde(self,x,usekron=True):
        """
        Takes a 2d-array (preferibly (N,DIM)) or list (of array of points for each dimension)
        If kron == True : take kron product of 1D vandermonde matrices
        If kron == False : take column multiplication of 1D matrices
        """
        
        if type(x) == list:
            x = np.array(x);
        
        if (x.shape[0] == self.DIM) and (x.shape[1] != self.DIM):
            x = x.T;
        
        if (x.shape[1] != self.DIM) :
            print "The number of elements in x is not consistent with the dimension of the element"
            return
        
        if (x.shape[0] == 0):
            print "The number of points in x is 0."
            return
        
        if usekron:
            VKron = np.array([1.]);
            for d in range(0,self.DIM):
                VKron = np.kron(VKron, self.Vandermonde1D(x[:,d],d));
        else:
            VKron = np.ones((x.shape[0],1))
            for d in range(0,self.DIM):
                VKronNew = np.zeros((VKron.shape[0],VKron.shape[1] * (self.Ns[d]+1)))
                V = self.Vandermonde1D(x[:,d],d);
                for col in range(0,VKron.shape[1]):
                    VKronNew[:,col*(self.Ns[d]+1):(col+1)*(self.Ns[d]+1)] = np.tile(VKron[:,col],(self.Ns[d]+1,1)).T * V
                VKron = VKronNew
        return VKron;
    
    def GammaPower(self,power):
        maxBasis = self.VEl.shape[1];
        dims = np.ones(power) * maxBasis;
        EIdxs = list(itertools.product(*[range(0,maxBasis) for i in range(0,power)]));
        E = np.zeros(dims);
        # Compute the number of gauss points needed in order to get exact approximation
        Ngauss = [];
        for N in self.Ns:
            Ngauss.append( int(np.ceil( power*N/2. )) );
        
        # Compute recursion coefficients for the number of gammas required
        poly1D = [];
        x1D = [];
        w1D = [];
        vals1D = [];
        V1D = [];
        for d in range(0,self.DIM):
            dist = self.dists[d];
            N = Ngauss[d];
            eld = self.el[d];
            distCond = self.distsCond[d];
            
            # Scale the element using user provided function
            elSC = distCond(eld, 1);
            
            # Prepare the measure function
            if (abs(eld[0]) == np.inf) or (abs(eld[1]) == np.inf):
                # No mapping to [-1,1]. TAILS ARE ASSUMED TO GET RAPIDLY TO 0
                def wf_cap(y,i):
                    return dist.pdf(distCond(y,-1))/self.prEl;
            else:
                def wf_cap(y,i):
                    centEl = (eld[1] + eld[0])/2.;
                    dimEl = (eld[1]-eld[0]);
                    return dist.pdf(y * dimEl/2. + centEl)/self.prEl * dimEl * 0.5**self.DIM;
            
            # Generate basis and Gauss points
            ncapm = 500;
            mc = 1;
            mp = 0;
            xp = np.array([]);
            yp = np.array([]);
            irout = 0; # 1: Use sti internally, 0: Use lancz
            if (abs(elSC[0]) == np.inf) or (abs(elSC[1]) == np.inf):
                # Do not apply scaling (we assume tails decay!!)
                x = elSC;
                if (abs(elSC[0]) == np.inf): finl = False; 
                else: finl = True;
                if (abs(elSC[1]) == np.inf): finr = False; 
                else: finr = True;
            else:
                x = np.linspace(-1.,1.,mc+1);
                centEl = (elSC[1] + elSC[0])/2.;
                dimEl = (elSC[1]-elSC[0])/2.;
                finr = True;
                finl = True;
            endl = x[:-1];
            endr = x[1:];
            
            params = (ncapm, mc, mp, xp, yp, wf_cap, irout,finl,finr,endl,endr)
            P = Spectral1D.Poly1D(Spectral1D.ORTHPOL,params)
            
            self.poly1D.append(P)
            
            (xg,wg) = P.GaussQuadrature(N)
            wg /= np.sum(wg);
            
            if finl and finr:
                x = xg * dimEl + centEl;
                x1D.append(x);
            else:
                x = xg;
                x1D.append(x);
            w1D.append(wg);
            vals1D.append(distCond(x,-1));
            
            VCap = self.Vandermonde1D(vals1D[-1],d);
            V1D.append(VCap);
        
        # Compute tensor product of the Vandermonde matrices and weights
        wKron = np.array([1]);
        VKron = np.array([1]);
        for d in range(0,self.DIM):
            wKron = np.kron(wKron, w1D[d]);
            VKron = np.kron(VKron, V1D[d]);
        
        # Compute recursion coeff
        for idx in EIdxs:
            prod = VKron[:,idx[0]];
            for i in range(1,power):
                prod = prod * VKron[:,idx[i]];
            E[idx] = np.dot(prod,wKron);
        
        return E;
    
    def isInElement(self,x):
        """
        Takes a 2d-array (preferibly (N,DIM)) or list (of array of points for each dimension)
        """
        
        if type(x) == list:
            x = np.array(x);
        
        if (x.shape[0] == self.DIM) and (x.shape[1] != self.DIM):
            x = x.T;
        
        if (x.shape[1] != self.DIM) :
            print "The number of elements in x is not consistent with the dimension of the element"
            return
        
        # Check belonging
        belonging = np.ones(x.shape[0],dtype=bool); # Init all true
        for d in range(0,self.DIM):
            elBelonging = np.all([(x[:,d] >= self.el[d][0]),(x[:,d] < self.el[d][1])],axis=0)
            belonging = np.all([belonging, elBelonging], axis=0)
        return belonging
    
    def refresh(self,allocBasis=True):
        self.__InitBasis1D(allocBasis);
        self.__InitTensor(allocBasis);
        self.dirty = False;

class MEPCM_Forest:
    DIM = 0;
    elements = [];
    dists1D = [];
    distsCond1D = [];
    
    def __init__(self, el1D=None, dists1D=None, distsCond1D=None, Ns1D=None):
        if el1D == None:
            self.elements = [];
            self.DIM = 0;
            return
        
        if (len(el1D) != len(dists1D) or len(dists1D) != len(Ns1D) or len(Ns1D) != len(distsCond1D)) :
            print "The number of elements in el1D, dists1D, distsCond1D is not consistent"
            return

        self.DIM = len(el1D);
        self.dists1D = dists1D;
        self.distsCond1D = distsCond1D;
        
        self.elements = self.split(el1D, Ns1D);
    
#    def __reduce__(self):
#        return (MEPCM_Forest, (None,None,None,None), self.__getstate__());
    
    def __getstate__(self):
        return dict(DIM = self.DIM,
                    elements = [e.getstate() for e in self.elements])
#                    dists1D = self.dists1D,
#                    distsCond1D = self.distsCond1D)
    
    def __setstate__(self,state,dists=None,distsCond=None):
        self.DIM = state['DIM'];
        self.elements = []
        self.dists1D = dists;
        self.distsCond1D = distsCond;
        for e in state['elements']:
            el = MEPCM_Element([],[],[],[]);
            el.setstate(e,dists,distsCond);
            self.elements.append(el);
    
    def getstate(self):
        return self.__getstate__();
    
    def setstate(self,state,dists=None,distsCond=None):
        self.__setstate__(state,dists,distsCond);
    
    def split(self, el1D, Ns1D):
        elsIdx = [];
        for d in range(0,self.DIM):
            elsIdx.append(range(0,len(el1D[d])));
        elsIdxList = list(itertools.product(*elsIdx));
        
        root = [];
        for e in range(0,len(elsIdxList)):
            elsIdx = elsIdxList[e];
            el = []; # Coordinates for the element in each dimension
            Ns = [];
            for d in range(0,self.DIM):
                el.append( el1D[d][elsIdx[d]] );
                Ns.append( Ns1D[d][elsIdx[d]] );
            newEl = MEPCM_Element(el,self.dists1D,self.distsCond1D,Ns);
            newEl.refresh();
            root.append( newEl );
        return root;
    
    def refine(self, toRefIndices, toRefDims, toRefOrders):
        """
            ``refineOrder``: 0 = let the order be equal to the parent element. 1 = drop the order of 1
        """
        refinedIndices = [];
        for toRefIdx, toRefDim, toRefOrder in zip(reversed(toRefIndices),reversed(toRefDims),reversed(toRefOrders)):
            el = self.elements[toRefIdx].el;
            Ns = self.elements[toRefIdx].Ns;
            for d in range(0,self.DIM):
                if toRefDim[d]:
                    eld = el[d];
                    if (abs(eld[0]) == np.inf) or (abs(eld[1]) == np.inf):
                        print "Error: you are trying to refine an infinite element"
                        return
                    dimEld = eld[1]-eld[0];
                    el[d] = [np.array([eld[0],eld[0]+dimEld/2.]),np.array([eld[0]+dimEld/2.,eld[1]])];
                    Ns[d] = [toRefOrder[d],toRefOrder[d]];
                else:
                    el[d] = [el[d]];
                    Ns[d] = [toRefOrder[d]];
            newEls = self.split(el,Ns);
            
            self.elements.pop(toRefIdx);
            for newEl, i in zip(reversed(newEls), range(0,len(newEls))):
                self.elements.insert(toRefIdx,newEl);
                if i > 0:
                    for j in range(0,len(refinedIndices)):
                        refinedIndices[j] = refinedIndices[j] + 1
                refinedIndices.append(toRefIdx);
        return list(reversed(refinedIndices));
 
def UQ_MEPCM_Tensor(domain,solve,params,solvePostProcessing,paramUpdate,refOrder,minRefOrd=2,maxRefOrd=2,iMax=10,gamma=0.5,theta1=1e-2, theta2=.75):
    """
    DESCRIPTION:
        UQ_MEPCM_Tensor(solve,params,solvePostProcessing,dists,paramUpdate,polys,distsPoly,N,method)
        Performs Uncertainty Quantification analysis of the system described by rhs using the Probabilistic Collocation Method by Tensor Product of the random space.
    INPUT:
        ``domain``: (MEPCM_Forest object) initial domain on which to evaluate the functions
        ``solve``: function handle to the experiment to be quantified. Signature: sol = solve(sample,params)
        ``params``: parameters to be passed to the ODE system (these contain the uncertain parameter as well)
        ``solvePostProcessing``: post processing function called after all the simulation have been run. Signature: ``solsEl = solvePostProcessing(solsEl)``. It returns properly aligned solutions per element, meaning that for the solutions in each element solsEl[i] contains an [Ncoll x NDOF] array.
        ``paramUpdate``: function handle for updating the set of uncertain parameters. Signature: params = paramUpdate(params,sample)
        ``refinement``: 0 = No refinement, 1 = refinement + partial limiting, 2 = refinement + final limiting
        ``iMax``: maximum number of refinement iterations
        ``gamma``: parameter for adaptivity refinement criteria
        ``theta1``: parameter for adaptivity refinement criteria
        ``theta2``: parameter for the dimensional refinement criteria
    OUTPUT: dictionary with the following attributes
        ``domain``: MEPCM_Forest object
        ``solsEl``: (list #<multi-dim El>) solutions at collocation points per each element
        ``meanSol``: estimated mean
        ``varSol``: estimated variance
        ``uHatEl``: (list #<multi-dim El>) Galerkin coefficients (available only if method == 'projection')
        ``fEval``: total number of solve evalutations
    """

    from mpi4py import MPI
    
    comm = MPI.COMM_WORLD
    myrank = comm.Get_rank()
    
    ###################################################################################
    #                              PRE - PROCESSING                                   #
    ###################################################################################
        
    def action(sols,sol):
        sols.append(sol)
        return sols
    
    iLoop = 0;
    stopCrit = False;
    toRefIndices = [];
    refinedIdx = range(0,len(domain.elements));
    solsEl = [];
    totComputations = 0;
    while not stopCrit and (iLoop<iMax):
        iLoop = iLoop+1
        
        if myrank == 0:
            print "Total number of new elements: %d" % len(refinedIdx);
            table = PrettyTable(['#el','PrEl','refined']);
            for eli in range(0,len(domain.elements)):
                table.add_row([eli, domain.elements[eli].prEl, (eli in refinedIdx)])
            print table
        
        ###################################################################################
        #                             LOOP SIMULATION                                     #
        ###################################################################################
        
        # Merge all the collocation points
        vals = np.zeros((0,domain.DIM))
        splitSizes = [];
        for eli in refinedIdx:
            vals = np.vstack((vals,domain.elements[eli].valsEl));
            splitSizes.append(domain.elements[eli].valsEl.shape[0]);
        splitPos = np.cumsum(splitSizes)
        totComputations += vals.shape[0];
        
        # Run the experiments
        sols = run_experiments(solve, vals, params, paramUpdate, action);
        
        if myrank == 0:
            # Split solutions by element
            solsElSplit = np.split(sols,splitPos[:-1],axis=0);
            
            # Insert new sols in solsEl
            for eli,i in zip(refinedIdx,range(0,len(refinedIdx))):
                solsEl.insert(eli,solsElSplit[i]);
        
        solsEl = comm.bcast(solsEl, root=0);
    
        ###################################################################################
        #                             LOOP POST-PROCESSING                                #
        ###################################################################################
        
        if myrank == 0:
            # COMPUTE COEFFICIENTS of expansion
            nEls = len(domain.elements);
            uHat = [];
            sigmaEl = [];
            etaEl = [];
            for i in range(0,nEls):
                uh = la.solve(domain.elements[i].VEl,solsEl[i])
                uHat.append( uh )
                if len(solsEl[i]) > 1:
                    Np = min(domain.elements[i].Ns)-1
                    orderList = np.array([sum(o) for o in domain.elements[i].orderEl])
                    gammas = np.dot(domain.elements[i].wEl,domain.elements[i].VEl*domain.elements[i].VEl)
                    sigma2bar = np.dot(uh[1:]**2., gammas[1:] )
                    sigmaEl.append( sigma2bar )
                    if sigma2bar != 0.:
                        eta = np.dot(uh[orderList >= Np]**2., gammas[orderList >= Np]) / sigma2bar
                        etaEl.append( eta );
                    else: etaEl.append(0.);
                else:
                    sigmaEl.append(0.);
                    etaEl.append(0.);
                
            # Check stopping criteria
            toRefIndices = [];
            toRefDims = [];
            toRefOrders = []; # Order change in each dimension
            stopCrit = True;
            if (iLoop < iMax):
                for eli in reversed(range(0,len(uHat))):
                    if (etaEl[eli]**gamma * domain.elements[eli].prEl >= theta1):
                        toRefIndices.append(eli);
                        # Detect the dimension to be refined
                        dimSens = np.zeros(domain.DIM);
                        orderEl = np.array(domain.elements[eli].orderEl)
                        orderList = np.array([sum(o) for o in domain.elements[eli].orderEl])
                        for d in range(0,domain.DIM):
                            Np = domain.elements[eli].Ns[d]-1
                            NpIdx = (orderEl[:,d] == Np) * (orderList == Np);
                            gammaNp = np.dot(domain.elements[eli].wEl,domain.elements[eli].VEl[:,NpIdx]*domain.elements[eli].VEl[:,NpIdx])
                            dimSens[d] = (uHat[eli][NpIdx][0] * gammaNp[0])/ (etaEl[eli] * sigmaEl[eli]);
                        
                        maxSens = np.amax(np.abs(dimSens));
                        refDims = np.zeros(domain.DIM,dtype=bool);
                        refOrders = np.zeros(domain.DIM,dtype=int);
                        for d in range(0,domain.DIM):
                            if domain.elements[eli].finite1D[d] and (np.abs(dimSens[d]) >= theta2 * maxSens):
                                refDims[d] = True;
                                refOrders[d] = max(minRefOrd,min(domain.elements[eli].Ns[d]+refOrder,maxRefOrd));
                            else:
                                refDims[d] = False;
                                # Check eta condition for lower coefficients
                                Np = domain.elements[eli].Ns[d]-1; # Remember Ns-1 is the highest order
                                sens = 0.0;
                                while (Np > minRefOrd) and (np.abs(sens) < theta2 * maxSens):
                                    Np -= 1;
                                    NpIdx = (orderEl[:,d] == Np) * (orderList == Np);
                                    gammaNp = np.dot(domain.elements[eli].wEl,domain.elements[eli].VEl[:,NpIdx]*domain.elements[eli].VEl[:,NpIdx])
                                    sens = (uHat[eli][NpIdx][0] * gammaNp[0])/ (etaEl[eli] * sigmaEl[eli]);
                                refOrders[d] = Np+1;
                        
                        toRefDims.append(refDims);
                        toRefOrders.append(refOrders);
                        if (iLoop < iMax): solsEl.pop(eli);
                        stopCrit = False;
            
            toRefIndices = list(reversed(toRefIndices));
            toRefDims = list(reversed(toRefDims));
            toRefOrders = list(reversed(toRefOrders));
            
            table = PrettyTable(['#el','PrEl', 'eta', 'etaPr','toRefine']);
            for eli in range(0,len(domain.elements)):
                table.add_row([eli, domain.elements[eli].prEl, etaEl[eli], etaEl[eli]**gamma * domain.elements[eli].prEl, (eli in toRefIndices)])
            print table
            
            if not stopCrit and (iLoop<iMax):
                # Split elements (exclude tails)
                refinedIdx = domain.refine(toRefIndices,toRefDims,toRefOrders);
            
            domainState = domain.getstate()
        
        else:
            # Other processes
            domainState = [];
        
        stopCrit = comm.bcast(stopCrit, root=0);
        domainState = comm.bcast(domainState, root=0);
        refinedIdx = comm.bcast(refinedIdx, root=0);
        domain.setstate(domainState,domain.dists1D,domain.distsCond1D)
            
    ## END LOOPS ##
    
    if myrank == 0:
        print "Total number of experiments: %d" % totComputations
        
        # COMPUTE MEAN
        uHat0 = np.array([uHat[i][0] for i in range(0,len(uHat))]);
        prEls = np.array([domain.elements[i].prEl for i in range(0,len(domain.elements))]);
        meanSol = np.dot(uHat0, np.asarray(prEls));
        
        # COMPUTE VARIANCE
        varSol = np.dot( np.array(sigmaEl) + (uHat0 - meanSol)**2. , prEls)
        
        ###################################################################################
        #                              OUTPUT                                             #
        ###################################################################################
        # Prepare a dictionary with necessary data
        dictionary = {'domain': domain,
                      'solsEl': solsEl,
                      'meanSol': meanSol,
                      'varSol': varSol,
                      'uHatEl': uHat,
                      'fEval': totComputations}
        return dictionary
