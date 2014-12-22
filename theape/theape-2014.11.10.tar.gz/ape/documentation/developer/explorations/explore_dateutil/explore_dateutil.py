
# python standard library
import datetime

# third-party
from dateutil.relativedelta import relativedelta


time = datetime.datetime.now()
minutes = 5
expected = minutes * 60
delta = relativedelta(minutes=minutes)
actual = (time + delta - time).seconds
print expected == actual
