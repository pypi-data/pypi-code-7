import pyfde
import random
from math import cos, pi, exp, sqrt, e


# fitness function
def ackley(p):
    a, b = 0.0, 0.0
    t = 2.0*pi

    for v in p:
        a += v*v
        b += cos(t*v)

    n = len(p)
    return -(-20.0*exp(-0.2*sqrt(a/n)) - exp(b/n) + 20 + e)

# solver configuration
N_IT = 100
N_POP = 80
N_DIM = 30
rng = random.Random()
solver = pyfde.ClassicDE(ackley, n_dim=N_DIM, n_pop=N_POP, limits=(-32.0, 32.0),
                      seed=rng.randint(1, 9999))
solver.cr = 0.25
solver.f = 0.25

# run until the error is smaller than 1e-14
nffe = 0
print('Fitness evaluations | Total error')

for best, fit in solver(N_IT):
    nffe += N_POP*N_IT
    err = -fit
    print("{:<7d} {:>6.3g}".format(nffe, err))

    if err < 1e-13:
        break
