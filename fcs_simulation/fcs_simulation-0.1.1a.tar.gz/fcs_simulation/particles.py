
from __future__ import absolute_import, division
import numpy as np
from numpy.random import normal

from utils import Box
from diffusion_utils import max_sigma, sigma_from_dt, random_step, time_step, Gaussian
#from stats_utils import PDF_to_events

from units import NANO, MICRO, MILLI



class Particle(object):
    """Represents a single particle. Obtained from a particles object. A Particle just a view into the numpy arrays of the parent particles object.
    """
    def __init__(self, parent, index):
        """Called only from a Particles object"""
        self.parent = parent
        self.index = index
    
    @property
    # @quick_contract(returns=np.ndarray)
    def position(self):
        return self.parent.positions[self.index]
    
    @property
    # @contract(returns='float,>=0,<=1')
    def photon_PDF(self):
        """Normalized robability of this particle generating a detected photon.
        Returns: 
        float: Normalized probability density of this particle
        contributing a photon.
        """

        return Simulation.gaussian(self.position)
    # @contract(returns=np.ndarray)
    def step(self):
        I, t = self.parent.step_particle(self.index, self.parent.particleIntensities[self.index][1])
        return I, t
    def wrapBoundaries(pos, r):
        position = pos[:]
        for i in range(len(position)):
            position[i] = (position[i] + r)%(2*r) - r
        return position


class Particles(object):
    """Container of :py:class:Particle:s"""
    def __init__(self, count_particles, boundaries):
        """Create count_particles particles inside boundaries region"""
        self.count_particles = count_particles
        self.positions = (np.random.rand(count_particles, 3)*2-1)*boundaries.radius

        self.particle_intensities = np.zeros((count_particles, 2)) # [(most current (last) Intensity, next timestep)]
        for i in range(count_particles):
            self.setIntensity(i, self[i].photon_PDF, 0)

    # @contract(returns="int,>=0")
    def get_next_index(self):
        """Returns the index of the particle that is due to step next"""
        return min(range(self.count_particles), key=lambda i: self.particle_intensities[i][1])

    # @contract(returns=Particle)
    def get_next(self):
        """stuff"""
        return self[self.get_next_index()]

    # @contract(returns=Particle)
    def __getitem__(self, index):
        return Particle(self, index)

    # sum of the individual intensities
    def netIntensity(self):
        return np.sum(self.particle_intensities, axis=0)[0]

    # update individual intensity of ith particle with timestep
    def setIntensity(self, i, I, next_time):
        oldtime, oldintensity = self.particle_intensities[i]
        self.particle_intensities[i] = (I, next_time)
        return next_time

    

    # move particle and update individual intensity
    # TODO: move into Particle
    def step_particle(self, i, old_time):
        # move
        sigma = max_sigma(self.positions[i], self.experiment.beam_box,
                          min_sigma=sigma_from_dt(10*MILLI, Simulation.D(100*NANO)))

        toCyl = lambda x: np.array([np.sqrt(x[0]**2+x[1]**2), x[2]])

        oldI = self.netIntensity()
        oldPosition = toCyl(self[i].position)

        dt = time_step(sigma, Simulation.D(100*NANO))
        self.positions[i] = random_step(self.positions[i], sigma)
        self.positions[i] = wrapBoundaries(self.positions[i], Simulation.r)
        # intensity
        self.setIntensity(i, self[i].photon_PDF, old_time+dt)
        newI = self.netIntensity()

        return newI, old_time
