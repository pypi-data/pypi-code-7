#! /usr/bin/python
# -*- coding: utf-8 -*-
"""Diffussion of Droplets through Gaussian Beam.

Simulate droplets diffusing though a detection region with steps drawn
from a 3D gaussian with :math:`\sigma = <r^2> = 6 D \Delta t`

On ubuntu to install both fcs_simulation and Ben's photon-tools

.. code-block:: bash

  sudo apt-get install bison flex python-setuptools python-dev autoconf libtool zlib1g-dev texinfo gawk g++ curl texlive subversion make gettext
  pip install fcs_simulation  

Usage:

.. code-block:: bash

  python simulation.py -photon-tools -n 8000 -T 10 -photons 10000000

Install from source:

.. code-block:: bash

  git clone https://github.com/computemachines/FCS-Simulation.git
  cd FCS-Simulation
  sudo setup.py install

"""

from __future__ import absolute_import, division
import numpy as np
from numpy.random import normal

from .utils import Box
from .diffusion_utils import max_sigma, sigma_from_dt, random_step, time_step, Gaussian
#from stats_utils import PDF_to_events

from .units import NANO, MICRO, MILLI

from .particles import Particles, Particle

# from contracts import contract

# from quickcontract import quick_contract

# @quick_contract(n='(float|int),>=0')
# def sqrt(n):
#     return np.sqrt(n)

#@quick_contract(radius="(float|int),>=0")
class Boundaries(Box): # pylint: disable=too-few-public-methods
    """Abstracts the boundaries of the simulation. I might put something complex in here one day."""
    def __init__(self, radius):
        self.radius = radius
        Box.__init__(self, 2*radius, 2*radius, 2*radius)

class Simulation(object):
    """Simulates diffusing particles of constant radius from a solution of aspecified density or a specified total number of particles."""
    detection_volume = Gaussian(covariance_matrix=\
                                np.diag([200*NANO*200*NANO,
                                         200*NANO*200*NANO,
                                         2.7*MICRO*2.7*MICRO]))

    r = 10*MICRO
    @staticmethod
    def D(r): # pylint: disable=invalid-name
        """Returns diffusivity of droplet with specified radius"""
        return 2.66 * 10**-19 / r # m^2/s # diffusivity

    def step(self):
        """Step one particle in the simulation"""
        next_particle = self.particles.get_next()
        current_intensity, current_time = next_particle.step(self.T[-1])
        self.I.append(current_intensity)
        self.T.append(current_time)

    @staticmethod
    def num_droplets_from(experiment_radius, density, droplet_radius):
        """Compute total number of droplets from desired molarity"""
        return int(3*(2*experiment_radius)**3 * density /(4*np.pi*droplet_radius**3))

    def __init__(self, density=0.3,
                 droplet_radius=200*NANO,
                 num_droplets=None):
        self.num_droplets = num_droplets
        self.experiment_radius = 10 * MICRO
        if self.num_droplets == None:
            self.num_droplets = Simulation.num_droplets_from(self.experiment_radius, 
                                                             density, droplet_radius)
        if self.num_droplets > 10**9:
            raise Exception('Too many droplets, N = '+str(self.num_droplets))

        self.beam_box = Box(500*NANO, 500*NANO, 5*MICRO)
        self.particles = Particles(self, self.num_droplets,
                                   self.experiment_radius)
        self.T = [0]
        self.I = [self.particles.netIntensity()]

