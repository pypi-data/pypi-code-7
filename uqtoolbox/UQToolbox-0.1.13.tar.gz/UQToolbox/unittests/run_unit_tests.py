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

__all__ = ['RunUnitTests','RunTestKL1D','RunTestKL2D','RunTestRandomSampling','RunTestTimingPreFit']

def RunTestRandomSampling(maxprocs=None,PLOTTING=False):
    import TestRandomSampling
    TestRandomSampling.run(maxprocs,PLOTTING)

def RunTestKL1D(maxprocs=None,PLOTTING=False):
    import TestKL1D
    TestKL1D.run(maxprocs,PLOTTING)

def RunTestKL2D(maxprocs=None,PLOTTING=False):
    import TestKL2D
    TestKL2D.run(maxprocs,PLOTTING)

def RunTestTimingPreFit(maxprocs=None,PLOTTING=False):
    import TestTimingPreFit
    TestTimingPreFit.run(maxprocs,PLOTTING)

def RunUnitTests(maxprocs=None,PLOTTING=False):
    """ Runs all the unit tests.
    
    :params int maxprocs: If MPI support is enabled, defines how many processors to use.
    """
    RunTestRandomSampling(maxprocs,PLOTTING)
    RunTestKL1D(maxprocs,PLOTTING)
    RunTestKL2D(maxprocs,PLOTTING)
