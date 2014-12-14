import pyfde
from math import sin, sqrt


def fitness(p):
    sum = 0.
    for v in p:
        sum += v*sin(sqrt(abs(v)))
    return sum

if __name__ == "__main__":
    solver = pyfde.ClassicDE(fitness, n_dim=10, n_pop=50, limits=(-500., 500.))
    solver.cr, solver.f = 0.5, 0.8

    best, fit = solver.run(n_it=1000)
    print("Fitness: {:.2f}".format(fit))
    print("Best:\n", best)
