'''Demonstrates how to use a generator to implement stopping conditions'''
import pyfde


def fitness(p):
    x = p[0]
    return 0.5*x**3 - 4*(x+2)**2 + 3

if __name__ == "__main__":
    solver = pyfde.ClassicDE(fitness, n_dim=1, n_pop=30, limits=(-5., 5.), seed=50)

    # check for the stopping condition every 10 iterations
    last_best, last_fit, its = None, float("-inf"), 0

    for best, fit in solver(n_it=5):
        its += 5

        if fit > last_fit:
            last_best, last_fit = best, fit
        else:
            break

    print("Best solution found after {:d} iterations".format(its))
    print("x = {:.2f}, with fitness {:.2f}".format(last_best[0], last_fit))

    print("\n** All solutions **\n")

    for sol, fit in solver:
        print(sol, fit)
