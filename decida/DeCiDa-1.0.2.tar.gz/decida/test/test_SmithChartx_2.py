#!/usr/bin/env python
import user, decida, decida.test
from decida.Data import Data
from decida.SmithChartx import SmithChartx

test_dir = decida.test.test_dir()
d = Data()
d.read(test_dir + "spars.col")
h=SmithChartx(None, command=[d, "freq REAL(Sdd11) IMAG(Sdd11) REAL(Sdd22) IMAG(Sdd22) REAL(Sdd12) IMAG(Sdd12)"], symbols=["dot"])
