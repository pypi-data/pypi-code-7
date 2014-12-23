from pydse import data
from pydse.arma import ARMA
from pydse.utils import make_lag_arr
import pandas as pd
from pandas.stats.moments import rolling_mean

df = data.airline_passengers()
df['Trend'] = rolling_mean(df['Passengers'], window=36, min_periods=1)
residual_all = df['Passengers'] / df['Trend']
residual_known = residual_all[:-24]
pd.DataFrame({'future': residual_all, 'known': residual_known}).plot()