import pyfde
from pyfde.bench import schewefel_batch
from timeit import default_timer as timer


def benchit(n_times):
    init = timer()

    for _ in range(n_times):
        solver = pyfde.Solver(schewefel_batch, n_dim=10, n_pop=50,
                              limits=(-500., 500.), batch=True)
        solver.cr, solver.f = 0.5, 0.8
        _, _ = solver.run(n_it=1000)

    end = timer()
    return (end - init) / n_times

if __name__ == "__main__":
    print("Time per run: {:.3f} seconds".format(benchit(n_times=20)))
