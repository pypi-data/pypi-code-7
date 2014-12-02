import pyfde


def fitness(p):
    return p[0]**2 - p[1]**2

if __name__ == "__main__":
    # each dimension can have its own limits
    solver = pyfde.Solver(fitness, n_dim=2, n_pop=40,
                          limits=[(10., 20.), (-5., -2.)])

    b, fit = solver.run(n_it=50)
    print("**Best solution found**")
    print("x, y    = {:.1f}, {:.1f} (expected: 20., -2.)".format(b[0], b[1]))
    print("Fitness = {:.2f}".format(fit))
