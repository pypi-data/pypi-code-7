#!/usr/bin/env python
import user, decida, decida.test
from decida.Data import Data
from decida.DataViewx import DataViewx

test_dir = decida.test.test_dir()
d = Data()
d.read(test_dir + "smartspice_tr_binary.raw")
DataViewx(data=d, command=[["time v(cint) v(osc)", "ymin=0, ymax=4"],  ["time v(q_2)"]])
