AR = (np.array([1, .5, .3]), np.array([3, 1, 1]))
MA = (np.array([1, .2]), np.array([2, 1, 1]))
arma = ARMA(A=AR, B=MA, rand_state=0)