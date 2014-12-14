#!/usr/bin/env python
import user, decida, decida.test
from decida.Data import Data
from decida.DataViewx import DataViewx

test_dir = decida.test.test_dir()
d = Data()
d.read(test_dir + "lcosc.tr.col")
dx = d.period_time_average("time", "ivdd", period=70e-12)
DataViewx(data=dx, command=[["time avg"]])
