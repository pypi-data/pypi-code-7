# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
#  OpenModes - An eigenmode solver for open electromagnetic resonantors
#  Copyright (C) 2013 David Powell
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt

import os.path as osp

import openmodes
from openmodes.constants import c, eta_0
from openmodes.parts import ArrayPart, SinglePart

outer_radius = 4e-3

sim = openmodes.Simulation(name="example4")
srr_mesh = sim.load_mesh(osp.join(openmodes.geometry_dir, "SRR.geo"), 
                    parameters={'inner_radius': 2.5e-3, 'outer_radius': outer_radius},
                    mesh_tol=0.7e-3)


srr_part = SinglePart(srr_mesh)

a = ArrayPart(srr_mesh, num=(5), period=2.6)
