#! /usr/bin/python

import pickle
import numpy as np
import matplotlib.pyplot as plt

def autocorr(x):
    result = numpy.correlate(x, x, mode='full')
    return result[result.size/2:]

def getTrajs():
    return pickle.load( open('trajs.pickle', 'rb') )

def gaussBeamI(r, z, I_0=1.0, w_0=10.0, z_R=1.0):
    def w(z):
        return w_0*np.sqrt(1+(z/z_R)**2)
    return I_0*(w_0/w(z))**2 * np.exp(-2*r**2/w(z)**2)

def maskTraj(traj):
    intensities = []
    for (x,y,z) in traj:
        r = np.sqrt(x**2+y**2)
        intensities.append(gaussBeamI(r, z))
    return intensities

def maskTrajs(trajs):
    return np.sum([maskTraj(traj) for traj in trajs], axis=0)

def plotIntensites(intensities):
    for intensity in intensities:
        plt.plot(intensity)
    plt.plot(np.sum(intensities, axis=0), 'k--')
    plt.show()

if __name__=='__main__':
    plotIntensites([maskTraj(traj) for traj in getTrajs()])


# X_ = np.arange(-3.0, 3.0, 0.1)
# Y_ = np.arange(-3.0, 3.0, 0.1)
# X, Y = np.meshgrid(X_, Y_)

# Z = [[gaussBeamI(x,y) for y in Y_] for x in X_]

# plt.contour(X, Y, Z)

# plt.show()
