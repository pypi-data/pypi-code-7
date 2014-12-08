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
 Cut ANOVA
=========================================

Created on Wed Mar 13 09:03:41 2013

@author: Daniele Bigoni (dabi@dtu.dk)

Description
-----------

This module is used to construct High Dimensionar Model Representation using cut-HDMR based on spectral methods from the module :py:mod:`SpectralToolbox.Spectral1D`. Additionally the cut-HDMR can be used to compute the associated ANOVA-HDMR.

"""

import numpy as np

import itertools

from SpectralToolbox import SpectralND
from SpectralToolbox import Misc

class NestedGrid:
    
    def __init__(self,parents,XF,WF,V,X_DIM,tol):
        self.parents = []
        self.XF = None
        self.WF = None
        self.V = None       # Vandermonde matrix
        self.X_DIM = None
        self.X_DIM_NOT_OVER = None
        self.tol = None
        
        self.FX_NOT_OVER = None
        
        self.parents = parents  # List of Nested Sparse Grids that are parent to this
        self.XF = XF
        self.WF = WF
        self.V = V
        self.X_DIM = X_DIM
        self.tol = tol
        self.X_DIM_NOT_OVER = self.X_DIM[ np.logical_not(self.get_overlapping()), : ]
    
    def __getstate__(self):
        return dict(parents = self.parents,
                    XF = self.XF,
                    WF = self.WF,
                    V = self.V,
                    X_DIM = self.X_DIM,
                    X_DIM_NOT_OVER = self.X_DIM_NOT_OVER,
                    tol = self.tol,
                    FX_NOT_OVER = self.FX_NOT_OVER)
    
    def __setstate__(self,state):
        self.parents = state['parents']
        self.XF = state['XF']
        self.WF = state['WF']
        self.V = state['V']
        self.X_DIM = state['X_DIM']
        self.X_DIM_NOT_OVER = state['X_DIM_NOT_OVER']
        self.tol = state['tol']
        self.FX_NOT_OVER = state['FX_NOT_OVER']
    
    def get_overlapping(self):
        out = np.zeros(self.XF.shape[0],dtype=bool)
        for nsg in self.parents:
            out = np.logical_or( out, Misc.findOverlapping(self.X_DIM, nsg.X_DIM, self.tol) )
        return out
    
    def get_FX(self):
        FX = np.zeros(self.X_DIM.shape[0])
        overlapping = np.zeros(self.XF.shape[0],dtype=bool)
        for nsg in self.parents:
            over = Misc.findOverlapping(self.X_DIM, nsg.X_DIM, self.tol)
            FX[over] = nsg.get_FX();
            overlapping = np.logical_or( overlapping, over )
        FX[np.logical_not(overlapping)] = self.FX_NOT_OVER
        return FX


class CutHDMRGrid(NestedGrid):
    
    cutHDMR_vals = None
    ANOVA_HDMR_vals = None
    
    def __init__(self,parents,XF,WF,V,X_DIM,tol):
        NestedGrid.__init__(self,parents,XF,WF,V,X_DIM,tol)
        self.cutHDMR_vals = np.zeros(X_DIM.shape[0])
        self.ANOVA_HDMR_vals = np.zeros(X_DIM.shape[0])
    
    def __getstate__(self):
        dd = NestedGrid.__getstate__(self)
        dd.update(cutHDMR_vals = self.cutHDMR_vals, 
                  ANOVA_HDMR_vals = self.ANOVA_HDMR_vals)
        return dd
    
    def __setstate__(self,state):
        NestedGrid.__setstate__(self,state)
        self.cutHDMR_vals = state['cutHDMR_vals']
        self.ANOVA_HDMR_vals = state['ANOVA_HDMR_vals']

class CutHDMR:
    
    grids = None
    idxs = None
    tol = None
    
    def __init__(self,polys,Ns,cut_order,X_cut,tol=1e-11):
        
        self.tol = tol
        
        DIM = len(polys)
        idxs_range = range(DIM)
        self.grids = []    # List of sparse grids
        self.idxs = []   # List of indices
        
        # Insert the zero term on the cut
        XF = X_cut.copy()
        WF = np.ones(1)
        V = np.ones(1)
        X_DIM = X_cut.copy()
        self.idxs.append(list(itertools.combinations(idxs_range,0)))
        self.grids.append( [CutHDMRGrid([],XF,WF,V,X_DIM,self.tol)]  )
        
        for order in range(1,cut_order+1):
            
            # Compute index lists
            idxs = list(itertools.combinations(idxs_range,order))
            self.idxs.append(idxs)
            
            SUB_GS_LIST = []
            for i, idx in enumerate(idxs):
                # order here is intended as integration dimension (so order 0 is integration on a point, order 1 is along a line, etc.)
                # Construct sparse grid of level ORD and dimension 'order'
                poly_list = [polys[j] for j in idx]
                Ns_list = [Ns[j] for j in idx]
                pND = SpectralND.PolyND(poly_list)
                (XF,WF) = pND.GaussQuadrature(Ns_list, normed=True)
                V = pND.GradVandermonde(XF,Ns_list,[0 for j in idx],usekron=False)
                
                # Plug the sparse grid in the correct cut in the DIM dimensional space
                X_DIM = np.tile(X_cut.copy(),(XF.shape[0],1))
                X_DIM[:,np.asarray(idx)] = XF
                
                # Find parent sparse grids of order-1
                idxs_parents = list(itertools.combinations(idx,order-1))
                parents = []
                for idx_parent in idxs_parents:
                    pointer_to_parent = self.idxs[order-1].index(idx_parent)
                    parents.append(self.grids[order-1][pointer_to_parent])
                
                SUB_GS_LIST.append( CutHDMRGrid(parents, XF, WF, V, X_DIM, self.tol) )
            
            self.grids.append(SUB_GS_LIST)
    
    def __getstate__(self):
        return dict(grids = self.grids,
                    idxs = self.idxs,
                    tol = self.tol)
    
    def __setstate__(self,state):
        self.grids = state['grids']
        self.idxs = state['idxs']
        self.tol = state['tol']
    
    def get_grids(self):
        return self.grids
    
    def get_idxs(self):
        return self.idxs
    
    def evaluateFun(self, f, transformFunc):
        for sub_sgs_list in self.grids:
            for nest_sg in sub_sgs_list:
                nest_sg.FX_NOT_OVER = f(transformFunc(nest_sg.X_DIM_NOT_OVER))
    
    def computeCutHDMR(self):
        """
        Computes the terms f0, f_i, f_ij, etc. and assign them to the ``CutHDMRGrid``s.
        """
        
        # Start from level zero and go up.
        for order_grids,order_idxs in zip(self.grids,self.idxs):
            for level_grid, level_idxs in zip(order_grids,order_idxs):
                # level_grid: grid on which we are computing the CutHDMR
                # level_idxs: indexs associated with the level_grid
                
                # HDMR projection: f^ij(x_i,x_j) - P_i f(x) - P_j f(x) - P_0 f(x)
                level_grid.cutHDMR_vals = level_grid.get_FX()
                # Find all the subsets of level_idxs and subtract to the cutHDMR_vals
                for idxs in Misc.powerset(level_idxs):
                    if idxs != level_idxs:
                        if idxs == ():
                            subgrid = self.grids[0][0]
                            level_grid.cutHDMR_vals -= subgrid.cutHDMR_vals
                        else:
                            # Lookup for the subgrid
                            order_subgrid = len(idxs)
                            idx_subgrid = self.idxs[order_subgrid].index(idxs)
                            subgrid = self.grids[order_subgrid][idx_subgrid]
                            
                            # Find where to subtract the values
                            # Look for the values with the same idxs coordinates
                            level_grid_Xfilt = level_grid.X_DIM[:,list(idxs)]
                            subgrid_Xfilt = subgrid.X_DIM[:,list(idxs)]
                            for X,val in zip(subgrid_Xfilt,subgrid.cutHDMR_vals):
                                isEqual = Misc.almostEqualList(level_grid_Xfilt,X,self.tol)
                                level_grid.cutHDMR_vals[isEqual] -= val
        
    def computeANOVA_HDMR(self):
        """
        Computes the terms f_0, f_i, f_ij, etc. and assign them to :py:data:`CutHDMRGrid.ANOVA_HDMR_vals`.
        """
        
        # Start from level zero and go up
        for order_grids,order_idxs in zip(self.grids,self.idxs):
            for level_grid, level_idxs in zip(order_grids,order_idxs):
                # level_grid: grid on which we are computing the ANOVA-HDMR
                # level_idxs: indexs associated with the level_grid
                
                # HDMR projection: \int_K^{n-l} f^cut(x) - P_i f(x) - P_j f(x) - P_0 f(x)
                # Compute the integral: iterate over the cuts and project onto the level_grid
                for inner_order_grids, inner_order_idxs in zip(self.grids,self.idxs):
                    for inner_level_grid, inner_level_idxs in zip(inner_order_grids,inner_order_idxs):
                        if level_idxs == ():
                            level_grid.ANOVA_HDMR_vals[0] += np.dot(inner_level_grid.cutHDMR_vals,inner_level_grid.WF)
                        else:
                            # project over the intersection betwenn level_idxs and order_idxs
                            inner_proj_idxs = set(inner_level_idxs).difference(set(level_idxs))
                            inner_cut_idxs = set(level_idxs).difference(inner_proj_idxs)                            
                            level_cut_idxs = set(level_idxs).intersection(inner_level_idxs)
                            
                            inner_proj_coord = inner_level_grid.X_DIM[:,np.asarray(list(inner_cut_idxs),dtype=int)]
                            level_proj_coord = level_grid.X_DIM[:,np.asarray(list(level_cut_idxs),dtype=int)]

                            (inner_proj_cut,inner_cut_idxs_list) = Misc.unique_cuts(inner_proj_coord, self.tol, retIdxs=True)
                            (level_proj_cut,level_cut_idxs_list) = Misc.unique_cuts(level_proj_coord, self.tol, retIdxs=True)
                            
                            # Project
                            for inner_prj_idxs,level_cut_idxs in zip(inner_cut_idxs_list,level_cut_idxs_list):
                                weights = inner_level_grid.WF[inner_prj_idxs]
                                weights /= np.sum(weights)
                                level_grid.ANOVA_HDMR_vals[level_cut_idxs] += np.dot( inner_level_grid.cutHDMR_vals[inner_prj_idxs], weights )
                
                
                # find all subsets of level_idxs and subtract to ANOVA_HDMR_vals
                for idxs in Misc.powerset(level_idxs):
                    if idxs != level_idxs:
                        if idxs == ():
                            subgrid = self.grids[0][0]
                            level_grid.ANOVA_HDMR_vals -= subgrid.ANOVA_HDMR_vals
                        else:
                            # Lookup for the subgrid
                            order_subgrid = len(idxs)
                            idx_subgrid = self.idxs[order_subgrid].index(idxs)
                            subgrid = self.grids[order_subgrid][idx_subgrid]
                            
                            # Find where to subtract the values
                            # Look for the values with the same idxs coordinates
                            level_grid_Xfilt = level_grid.X_DIM[:,list(idxs)]
                            subgrid_Xfilt = subgrid.X_DIM[:,list(idxs)]
                            for X,val in zip(subgrid_Xfilt,subgrid.ANOVA_HDMR_vals):
                                isEqual = Misc.almostEqualList(level_grid_Xfilt,X,self.tol)
                                level_grid.ANOVA_HDMR_vals[isEqual] -= val
    
