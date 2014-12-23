import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from pydse.arma import ARMA

AR = (np.array([1, .5, .3, 0, .2, .1, 0, .2, .05, 1, .5, .3]), np.array([3, 2, 2]))
MA = (np.array([1, .2, 0, .1, 0, 0, 1, .3]), np.array([2, 2, 2]))
arma = ARMA(A=AR, B=MA, rand_state=0)