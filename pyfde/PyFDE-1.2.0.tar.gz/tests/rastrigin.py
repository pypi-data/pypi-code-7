import pyfde
from math import cos, pi


def fitness(p):
    x, y = p[0], p[1]
    val = 20 + (x**2 - 10*cos(2*pi*x)) + (y**2 - 10*cos(2*pi*y))
    return -val

if __name__ == "__main__":
    solver = pyfde.ClassicDE(fitness, n_dim=2, n_pop=40, limits=(-5.12, 512))
    solver.cr, solver.f = 0.9, 0.45

    best, fit = solver.run(n_it=150)
    print("**Best solution found**")
    print("x, y    = {:.2f}, {:.2f} (expected: 0, 0)".format(best[0], best[1]))
    print("Fitness = {:.2f}".format(fit))
