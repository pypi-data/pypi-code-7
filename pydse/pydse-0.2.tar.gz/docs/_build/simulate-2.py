sim_data = arma.simulate(sampleT=100)
sim_index = pd.date_range('1/1/2011', periods=sim_data.shape[0], freq='d')
df = pd.DataFrame(data=sim_data, index=sim_index)
df.plot()