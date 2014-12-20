#! /usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

from simulation import Simulation, time_step

def show(title, array):
    hist, bins = np.histogram(array, bins=50)
    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2
    plt.bar(center, hist, align='center', width=width)
    plt.title(title)

    
    plt.show()

D = 1.0 * 10**-10

if __name__=="__main__":
    simulation = Simulation(numDroplets=10000)
    
    show('Particle position.x', simulation.particles.positions[:,0])
    show('Particle distance to box', 
         map(simulation.beam_box.dist, simulation.particles.positions))
    show('Particle current time step',
         np.log([time_step(sigma=simulation.particles.max_sigma(position),
                    diffusivity = D) for position in simulation.particles.positions]))
