from statsmodels.graphics.tsaplots import plot_pacf, plot_acf

sim_data = arma.simulate(sampleT=3000)
sim_index = pd.date_range('1/1/2011', periods=sim_data.shape[0], freq='d')
df = pd.DataFrame(data=sim_data, index=sim_index)
plot_acf(df[0], lags=10)
plot_pacf(df[0], lags=10)