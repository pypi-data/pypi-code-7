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

from auxiliary import bcolors

def print_ok(string):
    print bcolors.OKGREEN + "[SUCCESS] " + string + bcolors.ENDC

def print_fail(string,msg=''):
    print bcolors.FAIL + "[FAILED] " + string + bcolors.ENDC
    if msg != '':
        print bcolors.FAIL + msg + bcolors.ENDC

def run(maxprocs=None, PLOTTING = True):
    import numpy as np
    import numpy.linalg as npla
    from scipy import stats
    from UQToolbox import ModelReduction as MR
    from UQToolbox import RandomSampling as RS
    if PLOTTING:
        from matplotlib import pyplot as plt

    def kltest( C, span, title, NR ):

        NKL = [400]
        targetVar = 0.95
        KLE = MR.KLExpansion(C,1,span)
        KLE.fit(NKL,targetVar)
        print "UQToolbox.TestKL1D: " + title + " - KL-expansion length: %d" % KLE.nvars

        if PLOTTING:
            plt.figure()
            for i in range(min(5,NKL)):
                plt.plot(KLE.x[0],KLE.eigvecs[0][:,i])

            plt.figure()
            plt.semilogy(KLE.eigvals[0],'o-')

            # Draw some realizations
            NReal = 5
            Y = list( stats.norm(0,1).rvs(KLE.nvars*NReal).reshape((NReal,KLE.nvars)) )
            X = [KLE.scale(0,KLE.x[0])]
            proc = KLE.transform(X,Y)

            plt.figure()
            for i in range(NReal):
                plt.plot(KLE.x[0],proc[i])

        Y = list( RS.lhc(NR,KLE.nvars,[stats.norm(0,1) for i in range(KLE.nvars)]) )
        X = [KLE.scale(0,KLE.x[0])]
        proc = KLE.transform(X,Y)
        proc = np.asarray(proc)
        meanP = np.mean(proc[:,proc.shape[1]//2])
        varP = np.var(proc[:,proc.shape[1]//2])
        print "UQToolbox.TestKL1D: " + title + " - KLE Mean: %f    Var: %f" % (meanP,varP)

        if PLOTTING:
            meanF = np.mean(proc,axis=0)
            varF = np.var(proc,axis=0)
            plt.figure()
            plt.plot(KLE.x[0],meanF)
            plt.plot(KLE.x[0],meanF-np.sqrt(varF), '--r')
            plt.plot(KLE.x[0],meanF+np.sqrt(varF), '--r')
            plt.title( title + " - KLE - Mean and variance fields")

        xSc = ((KLE.x[0]+1.)/2. + span[0][0]) * (span[0][1] - span[0][0])
        GF = MR.GaussianField(C)
        GF.fit(xSc)
        Y = RS.lhc(NR,len(xSc), [stats.norm(0,1)] * len(xSc) )
        proc = GF.transform(Y)
        C_meanP = np.mean(proc[:,proc.shape[1]//2])
        C_varP = np.var(proc[:,proc.shape[1]//2])
        print "UQToolbox.TestKL1D: " + title + " - Cholesky Mean: %f    Var: %f" % (C_meanP,C_varP)

        if PLOTTING:
            meanF = np.mean(proc,axis=0)
            varF = np.var(proc,axis=0)
            plt.figure()
            plt.plot(KLE.x[0],meanF)
            plt.plot(KLE.x[0],meanF-np.sqrt(varF), '--r')
            plt.plot(KLE.x[0],meanF+np.sqrt(varF), '--r')
            plt.title( title + " - Cholesky - Mean and variance fields")

        if varP / 1.0 > targetVar:
            print_ok("UQToolbox.TestKL1D: 1D KL-expansion of " + title)
        else:
            print_fail("UQToolbox.TestKL1D: 1D KL-expansion of " + title,
                       "Percentage of expressed variance: %.2f%% [numerical estimate]" % (varP / 1.0 * 100.) )

        if PLOTTING:
            plt.show(block=False)

    NR = 10000
    span = [(0,1)]
    def C(x1,x2): return np.exp(-np.abs(x1-x2)/0.01)
    title = "Ornstein-Uhlenbeck Covariance"
    kltest(C,span,title,NR)

    span = [(0,1)]
    def C(x1,x2): return np.exp(-((x1-x2)**2.)/ (2. * 0.01**2.)) + 1e-12 * (x1==x2) # The last term is inserted to force it positive definite and avoid round-off errors
    title = "Squared Exponential Covariance"
    kltest(C,span,title,NR)



if __name__ == "__main__":
    # Number of processors to be used, defined as an additional arguement 
    # $ python TestKL.py N
    if len(sys.argv) == 2:
        maxprocs = int(sys.argv[1])
    else:
        maxprocs = None

    run(maxprocs)
