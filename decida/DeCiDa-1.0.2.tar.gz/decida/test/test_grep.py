#!/usr/bin/env python
import user, decida, decida.test
from decida.grep import grep

test_dir = decida.test.test_dir()
output = grep("Plotname", test_dir + "smartspice_dc_ascii.raw")
print output
