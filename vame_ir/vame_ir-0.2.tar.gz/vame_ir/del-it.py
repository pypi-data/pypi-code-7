__author__ = 'hamid'
import os
import sys
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(here)
from vame_ir import jalali
import datetime
d = datetime.date(2001,12,1)
a = jalali.to_jd(1393,7,16)
import time
t = time.time()
t = 1412807842 / (3600 * 24)
print(t)
print(jalali.jd_to(t))
import datetime
import _datetime
datetime.datetime
#testfdg d sgf gf
# jalali.
