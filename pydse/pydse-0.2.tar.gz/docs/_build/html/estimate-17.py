from pydse.arma import minic
from pydse.utils import make_lag_arr

best_ar_lags, best_ma_lags = minic([1, 11, 12, 13], [1, 11, 12, 13], residual)
arma = ARMA(A=make_lag_arr(best_ar_lags),
            B=make_lag_arr(best_ma_lags),
            rand_state=0)
arma.fix_constants()
arma.est_params(residual)
result = pd.DataFrame({'pred': arma.forecast(residual)[:, 0],
                       'truth': residual.values})
MAD = np.mean(np.abs(result['pred'][20:] - result['truth'][20:]))
result.plot(title="AR lags: {}; MA lags: {}; MAD: {}".format(
    ", ".join(map(str, best_ar_lags)), ", ".join(map(str, best_ma_lags)), MAD))