import pyfde
import random
from pyfde.bench import schewefel_batch
from timeit import default_timer as timer


def benchit(impl, n_times):
    init = timer()
    rng = random.Random()

    for t in range(n_times):
        if impl == "ClassicDE":
            solver = pyfde.ClassicDE(schewefel_batch, n_dim=10, n_pop=50,
                                  limits=(-500., 500.), batch=True)
            solver.cr, solver.f = 0.5, 0.8
        else:
            solver = pyfde.JADE(schewefel_batch, n_dim=10, n_pop=50,
                                  limits=(-500., 500.), batch=True)

        _, f = solver.run(n_it=1000)

    end = timer()
    return (end - init) / n_times

if __name__ == "__main__":
    for name in ["ClassicDE", "JADE"]:
        time = benchit(name, 50)
        print("Time per run {}: {:.3f} seconds".format(name, time))
