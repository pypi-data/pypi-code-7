#!/usr/bin/env python
import user, decida, decida.test
from decida.Data import Data
from decida.XYplotx import XYplotx

test_dir = decida.test.test_dir()
d = Data()
d.read(test_dir + "LTspice_ac_ascii.raw")
xyplot=XYplotx(None, command=[d, "frequency DB(V(vout1))"], title="AC analysis", xaxis="log", ymin=-60.0, ymax=0.0)

