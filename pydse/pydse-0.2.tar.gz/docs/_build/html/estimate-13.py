from pydse.arma import ARMA

AR = (np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.01]),
      np.array([13, 1, 1]))
MA = (np.array([1, 0.01, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.01]),
      np.array([14, 1, 1]))
arma = ARMA(A=AR, B=MA, rand_state=0)
arma.fix_constants()