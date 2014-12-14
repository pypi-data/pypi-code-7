#!/usr/bin/env python
import user, decida, decida.test
from decida.Data import Data
from decida.SmithChartx import SmithChartx

test_dir = decida.test.test_dir()
d = Data()
d.read_nutmeg(test_dir + "LTspice_ac_ascii.raw")
h=SmithChartx(None, command=[d, "frequency REAL(V(vout1)) IMAG(V(vout1))"])
