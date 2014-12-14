#!/usr/bin/env python
import user, decida, decida.test
from decida.Data import Data
from decida.XYplotx import XYplotx

test_dir = decida.test.test_dir()
d = Data()
d.read(test_dir + "smartspice_tr_binary.raw")
xyplot=XYplotx(None, command=[d, "time v(cint)"])
