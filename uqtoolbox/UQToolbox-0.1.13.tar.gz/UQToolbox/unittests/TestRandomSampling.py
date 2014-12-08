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
import numpy.linalg as npla
import scipy.stats as stats
import cPickle as pkl
import UQToolbox.RandomSampling as RS
from auxiliary import bcolors

def print_ok(string):
    print bcolors.OKGREEN + "[SUCCESS] " + string + bcolors.ENDC

def print_fail(string,msg=''):
    print bcolors.FAIL + "[FAILED] " + string + bcolors.ENDC
    if msg != '':
        print bcolors.FAIL + msg + bcolors.ENDC

def run(maxprocs=None, PLOTTING=True):
    if PLOTTING:
        import matplotlib.pyplot as plt
    
    # Test the convergence in mean of MC, LHC and Sobol for a 20 dimensional normal distribution
    dist = RS.MultiDimDistribution( [stats.norm()] * 20 )
    print_ok("UQToolbox.RandomSampling: MultiDimDistribution Construction")

    ns = 10 ** np.arange(1.,6.)
    dic = {'mc': [], 'lhc': [], 'sobol': []}
    for n in ns:
        n = int(n)
        dic['mc'].append( npla.norm( np.mean( np.asarray(dist.rvs(n)), axis=0 ) ) )
        dic['lhc'].append( npla.norm( np.mean( np.asarray(dist.lhc(n)), axis=0 ) ) )
        dic['sobol'].append( npla.norm( np.mean( np.asarray(dist.sobol(n)), axis=0 ) ) )
    
    print_ok("UQToolbox.RandomSampling: MultiDimDistribution Sampling")
    
    sl_mc = np.polyfit(np.log10(ns),np.log10(dic['mc']),deg=1)[0]
    sl_lhc = np.polyfit(np.log10(ns),np.log10(dic['lhc']),deg=1)[0]
    sl_sobol = np.polyfit(np.log10(ns),np.log10(dic['sobol']),deg=1)[0]

    print_ok("UQToolbox.RandomSampling: MultiDimDistribution Sampling convergence: MC %.2f, LHC %.2f, Sobol %.2f" % (sl_mc, sl_lhc, sl_sobol))
    
    if PLOTTING:
        plt.figure()
        plt.loglog(ns, ns**-.5, 'b--', label='O(N^-1/2)')
        plt.loglog(ns, ns**-1., 'k--', label='O(N^-1)')
        plt.loglog(ns,dic['mc'],'o-',label='mc')
        plt.loglog(ns,dic['lhc'],'o-',label='lhc')
        plt.loglog(ns,dic['sobol'],'o-',label='sobol')
        plt.legend()
        plt.xlabel('N')
        plt.ylabel('$\Vert E[x] \Vert$')
        plt.show(block=False)
    

    # Test the routines for the computation of the volume of the 6 dimensional unit ball
    d = 6
    def f(x,params):
        import numpy.linalg as npla
        return 1. if npla.norm(x) < 1. else 0.
    
    exact_vol = np.pi**3. / 6.
    store_file = 'rs.pkl'
    N1 = 987
    N2 = 98732
    store_freq = 100000

    # The experiment object
    experiments = RS.Experiments( f, \
                                  None, \
                                  [stats.uniform(0.,1.)] * d, \
                                  marshal_f = True, \
                                  store_file = store_file )
    print_ok("UQToolbox.RandomSampling: Experiments Construction")
    
    ##########################################
    # Test Monte Carlo
    experiments.sample( N1, 'mc' )
    print_ok("UQToolbox.RandomSampling: MC sampling")
    experiments.run(maxprocs, store_freq=store_freq)
    print_ok("UQToolbox.RandomSampling: MC evaluation")
    
    # Compute estimate
    est_vol = np.mean( experiments.get_results() ) * 2.**d
    print_ok("UQToolbox.RandomSampling: MC error (%d samples): %e" % ( len(experiments.get_results()), np.abs(exact_vol-est_vol)))
    
    # Reload from file
    ff = open(store_file,'rb')
    experiments = pkl.load(ff)
    ff.close()
    experiments.set_dists( [stats.uniform()] * d )
    print_ok("UQToolbox.RandomSampling: Reloading file")
    
    # Sample more
    experiments.sample( N2, 'mc' )
    print_ok("UQToolbox.RandomSampling: MC sampling more")
    experiments.run(maxprocs, store_freq=store_freq)
    print_ok("UQToolbox.RandomSampling: MC evaluation")
    
    # Compute estimate
    est_vol = np.mean( experiments.get_results() ) * 2.**d
    print_ok("UQToolbox.RandomSampling: MC error (%d samples): %e" % ( len(experiments.get_results()), np.abs(exact_vol-est_vol)))
    
    # Reset experiments
    experiments.reset()
    print_ok("UQToolbox.RandomSampling: reset")
    experiments.store()

    ##########################################
    # Test LHC
    experiments.sample( N1, 'lhc' )
    print_ok("UQToolbox.RandomSampling: LHC sampling")
    experiments.run(maxprocs, store_freq=store_freq)
    print_ok("UQToolbox.RandomSampling: LHC evaluation")
    
    # Compute estimate
    est_vol = np.mean( experiments.get_results() ) * 2.**d
    print_ok("UQToolbox.RandomSampling: LHC error (%d samples): %e" % ( len(experiments.get_results()), np.abs(exact_vol-est_vol)))
    
    # Reload from file
    ff = open(store_file,'rb')
    experiments = pkl.load(ff)
    ff.close()
    experiments.set_dists( [stats.uniform()] * d )
    print_ok("UQToolbox.RandomSampling: Reloading file")
    
    # Sample more
    experiments.sample( N2, 'lhc' )
    print_ok("UQToolbox.RandomSampling: LHC sampling more")
    experiments.run(maxprocs, store_freq=store_freq)
    print_ok("UQToolbox.RandomSampling: LHC evaluation")
    
    # Compute estimate
    est_vol = np.mean( experiments.get_results() ) * 2.**d
    print_ok("UQToolbox.RandomSampling: LHC error (%d samples): %e" % ( len(experiments.get_results()), np.abs(exact_vol-est_vol)))

    # Reset experiments
    experiments.reset()
    print_ok("UQToolbox.RandomSampling: reset")
    experiments.store()

    ##########################################
    # Test Sobol
    experiments.sample( N1, 'sobol' )
    print_ok("UQToolbox.RandomSampling: Sobol sampling")
    experiments.run(maxprocs, store_freq=store_freq)
    print_ok("UQToolbox.RandomSampling: Sobol evaluation")
    
    # Compute estimate
    est_vol = np.mean( experiments.get_results() ) * 2.**d
    print_ok("UQToolbox.RandomSampling: Sobol error (%d samples): %e" % ( len(experiments.get_results()), np.abs(exact_vol-est_vol)))

    # Reload from file
    ff = open(store_file,'rb')
    experiments = pkl.load(ff)
    ff.close()
    experiments.set_dists( [stats.uniform()] * d )
    print_ok("UQToolbox.RandomSampling: Reloading file")
    
    # Sample more
    experiments.sample( N2, 'sobol' )
    print_ok("UQToolbox.RandomSampling: Sobol sampling more")
    experiments.run(maxprocs, store_freq=store_freq)
    print_ok("UQToolbox.RandomSampling: Sobol evaluation")
    
    # Compute estimate
    est_vol = np.mean( experiments.get_results() ) * 2.**d
    print_ok("UQToolbox.RandomSampling: Sobol error (%d samples): %e" % ( len(experiments.get_results()), np.abs(exact_vol-est_vol)))


if __name__ == "__main__":
    # Number of processors to be used, defined as an additional arguement 
    # $ python TestKL.py N
    if len(sys.argv) == 2:
        maxprocs = int(sys.argv[1])
    else:
        maxprocs = None

    run(maxprocs)
