from pandas.stats.moments import rolling_mean
df['Trend'] = rolling_mean(df['Passengers'], window=36, min_periods=1)
df.plot()