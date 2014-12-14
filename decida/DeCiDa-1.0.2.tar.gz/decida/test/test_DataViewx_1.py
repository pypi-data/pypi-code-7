#!/usr/bin/env python
import user, decida, decida.test
from decida.Data import Data
from decida.DataViewx import DataViewx

test_dir = decida.test.test_dir()
d = Data()
d.read(test_dir + "LTspice_ac_ascii.raw")
DataViewx(data=d, command=[["frequency DB(V(vout1)) PH(V(vout1))", "xaxis=\"log\""]])
