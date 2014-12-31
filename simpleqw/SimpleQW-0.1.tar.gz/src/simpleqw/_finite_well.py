#
#   Copyright (c) 2014, Scott J Maddox
#
#   This file is part of SimpleQW.
#
#   SimpleQW is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   SimpleQW is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public
#   License along with SimpleQW.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#######################################################################

import numpy
from numpy import sqrt, tan, cos, pi, arcsin


def infinite_well_ground_state_energy(thickness, meff):
    '''
    thickness : float
        thickness of the well in units of meters
    meff : float
        effective mass in the well as a fraction of the electron mass

    Returns the ground state energy in units of eV.
    '''
    return 3.7603e-19 / (thickness ** 2 * meff)


def _finite_well_states(P):
    '''
    Returns the number of bound states in a finite-potential quantum well
    with the given well-strength parameter, `P`.
    '''
    return int(P / (pi / 2.)) + 1


def _finite_well_energy(P, n=1, atol=1e-6):
    '''
    Returns the nth bound-state energy for a finite-potential quantum well
    with the given well-strength parameter, `P`.
    '''
    assert n > 0 and n <= _finite_well_states(P)
    pi_2 = pi / 2.
    r = (1 / (P + pi_2)) * (n * pi_2)
    eta = n * pi_2 - arcsin(r) - r * P
    w = 1  # relaxation parameter (for succesive relaxation)
    while True:
        assert r <= 1
        if abs(eta) < atol:
            break
        r2 = r ** 2.
        sqrt_1mr2 = sqrt(1. - r2)
        denom = (1. + P * sqrt_1mr2)
        t1 = P * sqrt_1mr2 / denom * eta
#         t2 = -r * P / (2 * (1. + P * sqrt_1mr2) ** 3) * eta ** 2
        while True:
            next_r = (1 - w) * r + w * (r + t1)
#             next_r = (1 - w) * r + w * (r + t1 + t2)
            next_eta = n * pi_2 - arcsin(next_r) - next_r * P
            # decrease w until eta is converging
            if abs(next_eta / eta) < 1:
                r = next_r
                eta = next_eta
                break
            else:
                w *= 0.5

    alpha = P * r
    E = 2 * (alpha) ** 2  # hbar**2 / (m * L**2)
    return E

prefactor = 2.561584e9
def finite_well_energy(a, m, U, n=1):
    '''
    a : float
        thickness of the well in units of meters
    m : float
        effective mass in the well as a fraction of the electron mass
    U : float
        the potential in eV
    n : int
        the quantum number of the desired state

    If U <= 0, returns 0. Otherwise, returns the confinement energy in
    units of eV.

    Reference:
    D.L. Aronstein and C.R. Stroud, Jr., Am. J. Phys. 68, 943 (2000).
    '''
    if U <= 0.:
        return 0
    P = prefactor * a * sqrt(m * U)
    print P, _finite_well_energy(P, n)
    return _finite_well_energy(P, n) * 7.61996e-20 / m / a ** 2.

def plot_time():
    import time
    import matplotlib.pyplot as plt
    repeats = 20
    Pi = numpy.linspace(0.01, 6, 100)
    ti = numpy.empty_like(Pi)
    Eij = numpy.empty((100, repeats), dtype=float)
    for i in xrange(Pi.size):
        t0 = time.time()
        for j in xrange(repeats):
            Eij[i][j] = _finite_well_energy(Pi[i], n=1)
        t1 = time.time()
        ti[i] = float(t1 - t0) / repeats
#     print Pi
#     print ti
#     print Eij
    plt.semilogy(Pi, ti)
    plt.ylim(1e-5, 1e-1)
    plt.show()

def plot_E1():
    import matplotlib.pyplot as plt
    Pi = numpy.linspace(0, 6, 100)
    Ni = numpy.empty_like(Pi, dtype=int)
    for i, P in enumerate(Pi):
        Ni[i] = _finite_well_states(P)
    plt.plot(Pi, Ni)
    plt.show()
    plt.cla()
    Eij = numpy.empty((Pi.size, 10), dtype=float)
    for i, P in enumerate(Pi):
        for j in xrange(10):
            if j+1 <= _finite_well_states(P):
                Eij[i,j] = _finite_well_energy(P, n=j+1)
            else:
                Eij[i,j] = numpy.nan
    for j in xrange(10):
        plt.plot(Pi, Eij[:,j])
    plt.show()

if __name__ == '__main__':
#     plot_time()
#     plot_E1()
    print finite_well_energy(1e-9*1e-3, 1, 1, n=1)
