#!/usr/bin/env python
import user, decida, decida.test
import profile, pstats
from decida.Data import Data
from decida.XYplotx import XYplotx

print "This test is not yet functional"
if False :
    test_dir = decida.test.test_dir()
    d = Data()
    d.read(test_dir + "LTspice_ac_ascii.raw")
    profile.run("XYplotx(command=[d, \"frequency DB(V(vout1))\"])", "stats.pro")
    p = pstats.Stats("stats.pro")
    p.strip_dirs().sort_stats('time').print_stats()
