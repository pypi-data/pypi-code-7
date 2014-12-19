'''
This routine looks after the MPI-parallelization bits.
It takes care of the case that mpi4py is not available,
or that is it apparently available, but not useable.
'''

import os
from subprocess import check_call

FNULL = open(os.devnull, 'w')

try:
    check_call(['python','-c','from mpi4py import MPI'], stderr=FNULL)
    try:
        from mpi4py import MPI
        parallel = True
    except ImportError:
        parallel = False
except:
    #print ''
    #print 'MPI does not look usable directly, maybe a batch script is needed for it to work.'
    #print 'No worries, the serial version of the code is going to be used now.'
    #print ''
    parallel = False

if parallel:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
else:
    comm = None
    rank = 0
    size = 1
