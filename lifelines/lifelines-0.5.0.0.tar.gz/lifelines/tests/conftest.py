from __future__ import print_function
import numpy as np


def pytest_cmdline_main():
    seed = np.random.randint(1000)
    print("Seed used in np.random.seed(): %d" % seed)
    np.random.seed(seed)
