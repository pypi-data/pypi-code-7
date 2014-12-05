# EPCC
'''
This routine looks after the MPI-parallelization bits.
It takes care of the case that mpi4py is not available,
or that is it apparently available, but not useable.
'''
try:
    from mpi4py import MPI
    parallel = True
except ImportError:
    parallel = False

if parallel:
    from subprocess import check_call
    try:
        check_call(['python','-c','from mpi4py import MPI'])
    except:
        parallel = False

if parallel:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
else:
    comm = None
    rank = 0
    size = 1

