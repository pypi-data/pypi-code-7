#!/usr/bin/env python
import user, decida, decida.test
from decida.Data import Data
from decida.Histogramx import Histogramx

test_dir = decida.test.test_dir()
d = Data()
d.read(test_dir + "smartspice_tr_binary.raw")
h=Histogramx(None, command=[d, "v(cint)"], nbins=51)
