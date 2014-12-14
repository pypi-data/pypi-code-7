#!/usr/bin/env python
import user, decida, decida.test
from decida.Data import Data
from decida.DataViewx import DataViewx

test_dir = decida.test.test_dir()
d = Data()
d.read(test_dir + "smartspice_dc_ascii.raw")
d.set("i(vd) = - i(vd)")
DataViewx(data=d, command=[["vd i(vd)"],["vd i(vb)", "yaxis=\"log\""]])
