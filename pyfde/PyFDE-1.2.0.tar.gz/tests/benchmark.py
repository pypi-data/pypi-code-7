"""Benchmarks between the classic DE and JADE implementations, from Zhang, J.
et al, JADE : Adaptive Differential Evolution with Optional External Archive
"""

from collections import namedtuple
from functools import reduce
import pyfde
import operator

Function = namedtuple("Function", 'name fitness iterations limits')

def f1(vec):
    return -sum(x*x for x in vec)

def f2(vec):
    return -(sum(abs(x) for x in vec) +
            reduce(operator.mul, (abs(x) for x in vec), 1))

def f3(vec):
    acc, run = 0.0, 0.0
    for i in range(len(vec)):
        run += vec[i]
        acc += run * run
    return -acc

def f4(vec):
    return -max(abs(x) for x in vec)

functions = (
    Function(name="f1", fitness=f1, iterations=1500, limits=(-100, 100)),
    Function(name="f2", fitness=f2, iterations=2000, limits=(-10, 10)),
    Function(name="f3", fitness=f3, iterations=5000, limits=(-100, 100)),
    Function(name="f4", fitness=f4, iterations=5000, limits=(-100, 100)),
)

def make_classic(func):
    solver = pyfde.ClassicDE(func.fitness, n_dim=30, n_pop=100,
                           limits=func.limits)
    solver.f = 0.5
    solver.cr = 0.9
    return solver

def make_jade(func):
    solver = pyfde.JADE(func.fitness, n_dim=30, n_pop=100, limits=func.limits)
    solver.p = 0.05
    solver.c = 0.1
    return solver

for func in functions:
    print("**{}**".format(func.name))
    names = ("ClassicDE", "JADE")
    solvers = (make_classic(func), make_jade(func))

    for name, solver in zip(names, solvers):
        best, fit = solver.run(func.iterations)
        print("-> {}: {:g}".format(name, -fit))

    print()
