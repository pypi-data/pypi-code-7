import pandas as pd
result = pd.DataFrame({'pred': arma.forecast(residual)[:, 0],
                       'truth': residual.values})
MAD = np.mean(np.abs(result['pred'][20:] - result['truth'][20:]))
result.plot(title="AR lags: 12; MA lags: 1, 13; MAD: {}".format(MAD))