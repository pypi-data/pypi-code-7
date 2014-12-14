#!/usr/bin/env python
import user, decida
from decida.vtb import vtb

print "This test is not yet functional"
if False :
    testbench = "tb_bgp"
    netlistdir = "./%s_run1" % (testbench)
    vtb(netlistdir, testbench)
