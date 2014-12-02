import unittest
import pyfde
import numpy as np


class SanityTests(unittest.TestCase):

    def setUp(self):
        self.fitness = lambda p: -p[0] + p[1]
        self.n_dim = 2
        self.n_pop = 32
        self.limits = (-5., 5)
        self.solver = pyfde.Solver(self.fitness, self.n_dim, self.n_pop,
                                   self.limits)

    def test_solve(self):
        best, fit = self.solver.run(1000)
        self.assertAlmostEqual(best[0], self.limits[0])
        self.assertAlmostEqual(best[1], self.limits[1])
        self.assertAlmostEqual(fit, self.fitness(self.limits))

    def test_ranges(self):
        it = 0
        for best, fit in self.solver(10):
            it += 10
            if it > 1000:
                break

        self.assertGreater(it, 1000)
        best, fit = self.solver.run(0)
        self.assertEqual(len(best), self.n_dim)

        n = 0
        acc = 0
        for sol, fit in self.solver:
            n += 1
            acc += fit
            self.assertEqual(len(sol), self.n_dim)
            self.assertTrue(self.limits[0] <= sol[0] <= self.limits[1])
            self.assertTrue(self.limits[0] <= sol[1] <= self.limits[1])

        self.assertEqual(n, self.n_pop)
        self.assertAlmostEqual(acc / self.n_pop, self.fitness(self.limits))

    def test_limits(self):
        pyfde.Solver(self.fitness, 3, 5, (-3., 4.))
        pyfde.Solver(self.fitness, 3, 5, [(-1., 1.)]*3)
        pyfde.Solver(self.fitness, 3, 5, np.array([[-1, 1], [-1, 1],
                                                  [-1, 2]]))

        with self.assertRaises(AssertionError):
            pyfde.Solver(self.fitness, 3, 5, np.array([[-1, 1], [-1, 2]]))

        with self.assertRaises(AssertionError):
            pyfde.Solver(self.fitness, 0, 10, (-1, 1))

        with self.assertRaises(AssertionError):
            pyfde.Solver(None, 10, 10, (-1, 1))

        pyfde.Solver(self.fitness, 2, 5, (-1, 1))

        for p in range(4):
            with self.assertRaises(AssertionError):
                pyfde.Solver(self.fitness, 2, p, (-1, 1))


class BatchTest(unittest.TestCase):
    '''Tests the batch fitness evaluation.'''

    def setUp(self):
        self.solver = pyfde.Solver(self.fitness, 10, limits=(0, 10),
                                   batch=True)

    def fitness(self, pop, fit):
        for i, p in enumerate(pop):
            fit[i] = np.sum(p)

    def test_simple(self):
        best, fit = self.solver.run()
        self.assertAlmostEqual(fit, 10*10)
        np.testing.assert_allclose(best, np.array([10.0]*10))

if __name__ == '__main__':
    unittest.main()
