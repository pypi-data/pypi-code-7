import pyximport
import mpi4py
import numpy

import os
os.environ['CC'] = mpi4py.get_config()['mpicc']

pyximport.install(setup_args=dict(
        include_dirs=["./", mpi4py.get_include(), numpy.get_include()],
        script_args=[
        '--cython-include-dirs', ':'.join([mpi4py.get_include()])]
        )
        )

import failure
