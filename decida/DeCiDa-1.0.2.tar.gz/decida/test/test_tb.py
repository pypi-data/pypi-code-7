#!/usr/bin/env python
import user, decida, decida.test
from decida.tb import tb

print "This test is not yet functional"
if False :
    test_dir = decida.test.test_dir()
    netlistdir = test_dir
    spice_testbench_netlist   = netlistdir + "sar_seq_dig.net"
    verilog_testbench_netlist = netlistdir + "sar_seq_dig.v"
    tb(spice_testbench_netlist, verilog_testbench_netlist)
