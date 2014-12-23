df['Prediction'] = result['pred'].values * df['Trend'].values
del df['Trend']
df.plot()