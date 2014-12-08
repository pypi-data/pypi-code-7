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

def run(maxprocs=None, PLOTTING=False):
    import numpy as np
    import numpy.linalg as npla
    from scipy import stats
    from UQToolbox import ModelReduction as MR
    from UQToolbox import RandomSampling as RS
    if PLOTTING:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib import cm

    def kltest( C, spans, title, NR ):

        NKL = [400,400]
        targetVar = 0.95
        KLE = MR.KLExpansion(C,2,spans)
        KLE.fit(NKL,targetVar)
        print "UQToolbox.TestKL2D: " + title + " - KL-expansion length: %d" % KLE.nvars

        if PLOTTING:
            fig = plt.figure()
            X1,X2 = np.meshgrid(KLE.scale(1,KLE.x[1]),KLE.scale(0,KLE.x[0]))
            for i in range(9):
                ax = fig.add_subplot(3,3,i+1, projection='3d')
                Z = np.outer(KLE.eigvecs[0][:,KLE.order_valI[0,i]],KLE.eigvecs[1][:,KLE.order_valI[1,i]])
                ax.plot_surface(X1,X2,Z, cmap=cm.coolwarm,
                                linewidth=0, antialiased=False)
                plt.xlabel("x")
                plt.ylabel("y")
            fig.suptitle( title + " - basis functions")


            plt.figure()
            plt.semilogy(np.sort(KLE.tensor_valI,axis=None)[::-1],'o-')
            plt.title( title + " - decay of eigenvalues")

            # Draw some realizations
            Y = list( stats.norm(0,1).rvs(KLE.nvars*1).reshape((1,KLE.nvars)) )
            X = [ np.linspace(spans[0][0],spans[0][1],50), np.linspace(spans[1][0],spans[1][1],200) ]
            proc = KLE.transform(X,Y) 

            fig = plt.figure()
            plt.imshow(proc[0],origin='lower', extent=(spans[1] + spans[0]))
            plt.colorbar()
            plt.title(title + " - realization")

            plt.show(block=False)
            
        # Check represented variance at central point
        Y = list( RS.lhc(NR,KLE.nvars,[stats.norm(0,1) for i in range(KLE.nvars)]) )
        X = [ np.array([ (spans[0][0] + spans[0][1])/2. ]), np.array([ (spans[1][0] + spans[1][1])/2. ])]
        proc = KLE.transform(X,Y)
        proc = np.asarray(proc)
        meanP = np.mean(proc)
        varP = np.var(proc)
        print "UQToolbox.TestKL2D: " + title + " - KLE Mean: %f    Var: %f" % (meanP,varP)
                  
        if PLOTTING:
            X = [ np.linspace(spans[0][0],spans[0][1],10), np.linspace(spans[1][0],spans[1][1],40) ]
            proc = KLE.transform(X,Y)
            proc = np.asarray(proc)
            meanF = np.mean(proc,axis=0)
            varF = np.var(proc,axis=0)
            fig = plt.figure()
            X1,X2 = np.meshgrid(X[1],X[0])
            ax = fig.add_subplot(1,2,1, projection='3d')
            ax.plot_surface(X1,X2,meanF, cmap=cm.coolwarm,
                            linewidth=0, antialiased=False)
            plt.xlabel("x")
            plt.ylabel("y")
            ax = fig.add_subplot(1,2,2, projection='3d')
            ax.plot_surface(X1,X2,varF, cmap=cm.coolwarm,
                            linewidth=0, antialiased=False)
            plt.xlabel("x")
            plt.ylabel("y")
            fig.suptitle( title + " - KLE - Mean and variance fields")

        if varP / 1. > targetVar:
            print_ok("UQToolbox.TestKL2D: 2D KL-expansion of " + title)
        else:
            print_fail("UQToolbox.TestKL2D: 2D KL-expansion of " + title,
                       "Percentage of expressed variance: %.2f%% [numerical estimate]" % (varP / 1. * 100.) )

        if PLOTTING:
            plt.show(block=False)

    NR = 10000
    spans = [(0.,1.),(0.,4.)]
    def C(x1,x2): return np.exp(-np.abs(x1-x2)/0.1) 
    title = "Ornstein-Uhlenbeck Covariance"
    kltest(C,spans,title,NR)

    spans = [(0.,1.),(0.,4.)]
    def C(x1,x2): return np.exp(-(x1-x2)**2./ (2. * 0.1**2.)) + 1e-12 * (x1==x2)
    title = "Squared Exponential Covariance"
    kltest(C,spans,title,NR)



if __name__ == "__main__":
    # Number of processors to be used, defined as an additional arguement 
    # $ python TestKL.py N
    if len(sys.argv) == 2:
        maxprocs = int(sys.argv[1])
    else:
        maxprocs = None

    run(maxprocs)
