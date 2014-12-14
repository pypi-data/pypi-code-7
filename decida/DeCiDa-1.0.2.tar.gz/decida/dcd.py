################################################################################
# FUNCTION : dcd
# PURPOSE  : read SmartSpice netlist and control, generate python script
# AUTHOR   : Richard Booth
# DATE     : Sat Nov  9 11:19:00 2013
# -----------------------------------------------------------------------------
# NOTES    : 
#
# LICENSE  : (BSD-new)
# 
# This software is provided subject to the following terms and conditions,
# which you should read carefully before using the software.  Using this
# software indicates your acceptance of these terms and conditions.  If you
# do not agree with these terms and conditions, do not use the software.
# 
# Copyright (c) 2013 Richard Booth. All rights reserved.
# 
# Redistribution and use in source or binary forms, with or without
# modifications, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following Disclaimer
#       in each human readable file as well as in the documentation and/or
#       other materials provided with the distribution.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following Disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Richard Booth nor the names of contributors
#       (those who make changes to the software, documentation or other
#       materials) may be used to endorse or promote products derived from
#       this software without specific prior written permission.
# 
# Disclaimer
# 
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, INFRINGEMENT AND THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# ANY USE, MODIFICATION OR DISTRIBUTION OF THIS SOFTWARE IS SOLELY AT THE
# USERS OWN RISK.  IN NO EVENT SHALL RICHARD BOOTH OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, INCLUDING,
# BUT NOT LIMITED TO, CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# IN NO EVENT SHALL THE AUTHORS OR DISTRIBUTORS BE LIABLE TO ANY PARTY
# FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES
# ARISING OUT OF THE USE OF THIS SOFTWARE, ITS DOCUMENTATION, OR ANY
# DERIVATIVES THEREOF, EVEN IF THE AUTHORS HAVE BEEN ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# 
# THE AUTHORS AND DISTRIBUTORS SPECIFICALLY DISCLAIM ANY WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.  THIS SOFTWARE
# IS PROVIDED ON AN "AS IS" BASIS, AND THE AUTHORS AND DISTRIBUTORS HAVE
# NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR
# MODIFICATIONS.
################################################################################
import user
import decida
import string
import re
import os
import os.path
import shutil
import time
import stat
from decida.Tckt import Tckt

template = """#! /usr/bin/env python
###############################################################################
# NAME    : $SCRIPT
# PURPOSE : sequence file for simulation of $CIRCUIT
# DATE    : $DATE
# AUTHOR  : $AUTHOR
# -----------------------------------------------------------------------------
# NOTES:
#   * example tckt.monitor() specifications:
#     REF       : monitor voltage of node REF
#     VCD<3:0>  : monitor voltage of nodes VCD_3, ... , VCD_0
#     I(vsc)    : monitor current in voltage source vsc
#     IDN(mn1)  : monitor drain current in mosfet xmn1 (5V),    also IDN(xmn1)
#     IDNH(nmn1): monitor drain current in mosfet xmn1 (LDMOS), also IDNH(xnmn1)
#     IR(res)   : monitor current in resistor res, also IR(xres)
#     IX(xa1.p) : monitor current in subcircuit xa1, node p
#     PN(mn1-vdsat)  : monitor mosfet xmn1 vdsat parameter (5V)
#     PNH(mn1-vdsat) : monitor mosfet xmn1 vdsat parameter (LDMOS)
#     @Xgmc:    : following specs are for subcircuit Xgmc
#     @Xgmc.Xq: : following specs are for subcircuit Xgmc.Xq
#     @:        : following specs are for top-level circuit
#   * example tckt.element() definitions:
#     vin sin 0.6 0.2 $$freq
#     vbg netlist
#     vdd $$vdd
#     vsd<3:0> 5'b0011 v0=0.0 v1=$$vdd
#     vdac_in<9:0> counter v0=0.0 v1=$$vdd edge=$$edge hold=$$hold
#   * example Data commands:
#     d.set("z = v(out) * 2")
#     d.a2d("z", "v(sd<3:0>)", slice=1.5)
#     x = d.crossings("time", "v(xcp.cint)", level=1.5, edge="rising")
#     period = x[3] - x[2]
#   * stability analysis:
#     1. insert a voltage source in feedback path with + - in dir of feedback
#     2. in elements section, define the voltage source with stability spec.
#        a. example:
#            vstb stability xreg.xstb fmin=0.01 fmax=100G \\
#                method=middlebrook vblock=2 iblock=5
#        b. parameters:
#            xreg.xstb = full path of the stability source which is
#                to replace the voltage source
#            fmin, fmax = min, max frequency sweeps for ac analysis
#            method = middlebrook or vbreak
#            vblock, iblock = voltage and current simulation block numbers
#     3. no analysis card is required since stability analysis is signaled
#        by the voltage source element specification.  But doing an .op
#        analysis before the stability analysis seems to ensure dc conv.
#     4. in (post-process) report detail section, do stability_analysis
#           V = tckt.stability_analysis(plot=True, save=True)
#           phase_margin = V["pm"], etc.
###############################################################################
import user, decida, sys, string, re
from decida.Report  import Report
from decida.Data    import Data
from decida.Tckt    import Tckt
from decida.XYplotx import XYplotx
from decida.FrameNotebook import FrameNotebook
#==============================================================================
# test-circuit init
#==============================================================================
tckt = Tckt(project="$PROJECT", simulator="sspice", verbose=True)
tckt["testdir"] = "$TESTDIR"
tckt["path"] = [
    ".",
    "$PATH1",
]
tckt["temp_high"] = 125
postlayout = False
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# tests
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#==============================================================================
# tr: transient analysis
#==============================================================================
def tr(detail="simulate") :
    global tckt
    test      = tckt.get_test()
    modelfile = tckt.get_modelfile()
    tckt["circuit"]     = "$CIRCUIT"
    tckt["netlistfile"] = "$NETLIST"
    #--------------------------------------------------------------------------
    # signals to monitor
    #--------------------------------------------------------------------------
    tckt.monitor(\"\"\"
        $MONITOR
    \"\"\")
    #--------------------------------------------------------------------------
    # postlayout
    #--------------------------------------------------------------------------
    if postlayout :
        dir  = "$POSTLAYOUTDIR"
        file = "${CIRCUIT}_C_MAX_hier.spice"
        tckt.postlayout(\"X$CIRCUIT\", \"$CIRCUIT\", \"%s/%s\" % (dir, file))
    #--------------------------------------------------------------------------
    # loop through experiments
    #--------------------------------------------------------------------------
    poststart = True
    cases = $CASES
    if True :
        cases = ["$CASE0"]

    for case in cases :
        tckt["case"] = case
        ckey    = tckt.get_case_key()
        process = tckt.get_process()
        vdd     = tckt.get_vdd()
        temp    = tckt.get_temp()
        prefix  = "%s.%s.%s" % \\
            (test, tckt["circuit"], case)
        print prefix
        tckt["title"]  = prefix
        tckt["prefix"] = prefix
        tstop = 10e-6
        tstep = 1e-9
        tckt.elements(\"\"\"
            $ELEMENTS
        \"\"\")
        tckt.control(\"\"\"
            .options rawpts=150 nomod brief=1 probe
            .options itl1=50000 itl2=50000 gmin=0 dcpath=0
            .options conv=-1 accurate=1 gmin=0 dcpath=0
            .prot
            .lib '$$modelfile' $$process
            .unprot
            .temp $$temp
            .tr $$tstep $$tstop

            * gateway control lines:
            #com
            $CONTROL
            #endcom
        \"\"\")
        if   detail == "simulate" :
            if False and tckt.is_already_done() :
                continue
            tckt.generate_inputfile()
            tckt.simulate(clean=False)
        elif detail == "view" :
            if poststart :
                poststart = False
            if True :
                tckt.wait_for_data(2)
                tckt.view()
            else :
                if tckt.no_data() : continue
                d = Data()
                d.read_nutmeg(tckt.get_datafile())
                xy = XYplotx(command=[d, "time v(out)"])
        elif detail == "report" :
            if poststart :
                poststart = False
                point = 0
                rpt = Report(test + ".report", verbose=True, csv=True)
                header  = "point case temp vdd"
                rpt.header(header)
            if tckt.no_data() : continue
            d = Data()
            d.read_nutmeg(tckt.get_datafile())
            rpt.report(point, ckey, temp, vdd)
            point += 1
            del d
        else :
            print  "detail " + detail + " not supported"
#==============================================================================
# run specified tests
# all_test format:  test, details
# command-line argument format: test:detail or test (if no details)
#==============================================================================
all_tests = \"\"\"
    tr simulate view report
\"\"\"
tests = tckt.test_select(all_tests, sys.argv[1:])
for test in tests :
    eval(test)
exit()
"""

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# dcd function
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
def dcd(netlistdir, testbench, project=None, check=False, postlayoutdir=None):
    """ read SmartSpice netlist and control, generate python script.
    
    **arguments**:

        .. option:: netlistdir

                directory where netlist \*.net has been produced
    
        .. option:: testbench

                netlist prefix
    
        .. option:: check=False

                if True, produce check files for debugging
    
        .. option:: postlayoutdir=None

                directory with post-layout extractions

    **procedure**:

       1. create a top-level schematic in Gateway

          a. check all to detect any issues

          b. in simulation mode, check signals to be saved
             the schematic must be closed to have a \*.crb file be generated

          c. edit/modify the control file

       2. simulation->create netlist

       3. close the schematic so that \*.crb file is generated

       4. run create_sspice_script <testbench> (fill in parameters) 

          * creates <testbench>.py

       5. modify the python script and use to run simulations
    """
    spice_testbench_netlist = "%s/%s.net" % (netlistdir, testbench)
    spice_testbench_control = "%s/%s.ctr" % (netlistdir, testbench)
    spice_testbench_probes  = "%s/%s.crb" % (netlistdir, testbench)
    spice_testbench_params  = "%s/%s.defparams" % (netlistdir, testbench)
    local_testbench_params  =    "%s.defparams" % (testbench)
    if project is None or not project in Tckt.projects():
        print
        print "@" * 72
        print "%s is not in supported projects - changing project to GENERIC" % (project)
        print
        print "if using 1830AN18BA, use the AN18 project"
        print "if using 1860BD18BA, use the BD18 project"
        print
        print "the list of supported projects is:"
        ps = Tckt.projects()
        ps.sort()
        for p in ps:
            print p
        print "@" * 72
        PROJECT = "GENERIC"
    else :
        PROJECT = project
    TECH      = Tckt.project_tech(PROJECT)
    CASES     = str(Tckt.project_cases(PROJECT))
    CASE0     = Tckt.project_cases(PROJECT)[0]
    MODELFILE = Tckt.project_modelfile(PROJECT)
    try :
        USER = os.environ["USERNAME"]
    except :
        USER = os.environ["USER"]
    AUTHOR    = USER
    DATE      = time.asctime(time.localtime(time.time()))
    TESTDIR   = "/home/%s/work/%s/%s" % (USER, TECH, PROJECT)
    POSTLAYOUTDIR = "//projects/%s/" % (AUTHOR)
    if postlayoutdir :
        POSTLAYOUTDIR = postlayoutdir
    PATH1     = netlistdir
    #----------------------------------------------------------------------
    # output file:
    #----------------------------------------------------------------------
    output_file = string.lower(testbench) + ".py"
    NETLIST     = testbench + ".net"
    SCRIPT      = output_file
    CIRCUIT     = testbench
    m = re.search("^(TEST_|TB_TEST|TB_|test_|tb_test|tb_)(.+)$", testbench)
    if m :
        CIRCUIT = m.group(2)
    #----------------------------------------------------------------------
    # read spice netlist, eliminate continued lines and split into list
    # filter out comments
    #----------------------------------------------------------------------
    if not os.path.isfile(spice_testbench_netlist) :
        print "spice testbench netlist \"%s\" is not readable" % \
            (spice_testbench_netlist)
        exit()
    f = open(spice_testbench_netlist, "r")
    lines = f.read()
    f.close()
    lines = re.sub("\r", " ", lines)
    lines = re.sub("\n *\\+", " ", lines)
    lines = string.lower(lines)
    llines = string.split(lines, "\n")
    netlist_lines = []
    title = llines.pop(0)
    for line in llines :
        m = re.search("^ *\*", line)
        if m :
            continue
        line = re.sub("\$.*$", "", line)
        line = string.strip(line)
        if len(line) > 0 :
            netlist_lines.append(line)
    #----------------------------------------------------------------------
    # read spice control, eliminate continued lines and split into list
    #----------------------------------------------------------------------
    if not os.path.isfile(spice_testbench_control) :
        print "spice testbench control \"%s\" is not readable" % \
            (spice_testbench_control)
        #exit()
        control_lines = []
    else :
        f = open(spice_testbench_control, "r")
        lines = f.read()
        f.close()
        lines = re.sub("\r", " ", lines)
        lines = re.sub("\n *\\+", " ", lines)
        lines = string.lower(lines)
        control_lines = string.split(lines, "\n")
    #----------------------------------------------------------------------
    # read spice probes
    #----------------------------------------------------------------------
    if not os.path.isfile(spice_testbench_probes) :
        print "spice testbench probes \"%s\" is not readable" % \
            (spice_testbench_probes)
        #exit()
        probe_lines = []
    else :
        f = open(spice_testbench_probes, "r")
        lines = f.read()
        f.close()
        lines = re.sub("\r", " ", lines)
        probe_lines = string.split(lines, "\n")
    #----------------------------------------------------------------------
    # if defparams present, copy to local directory
    #----------------------------------------------------------------------
    if os.path.isfile(spice_testbench_params) :
        shutil.copyfile(spice_testbench_params, local_testbench_params)
    #----------------------------------------------------------------------
    # collect voltage sources and currents
    #----------------------------------------------------------------------
    elements = []
    for line in netlist_lines :
       m = re.search("^(v|i)", line)
       if m :
           tokens = string.split(line)
           name = tokens[0]
           elements.append(name + " " + "netlist")
    #----------------------------------------------------------------------
    # collect monitored wire names
    #----------------------------------------------------------------------
    names  = []
    for line in probe_lines :
       m = re.search("^\[Wire\.CURRENT_VOLTAGE\.([^\]]+)", line)
       if m :
           name = m.group(1)
           name = string.lower(name)
           names.append(name)
    names.sort()
    subckt = ""
    monitored = []
    line = ""
    for name in names :
        tokens = string.split(name, ".")
        if len(tokens) > 1 :
            name = tokens[-1]
            sc = string.join(tokens[0:-1], ".")
        else :
            sc = ""
        if sc != subckt :
            subckt = sc
            if len(line) > 0 :
                monitored.append(line)
            line = "@" + sc + ": "
        if len(line) > 64 :
            monitored.append(line)
            line = ""
        line += name + " "
    if len(line) > 0 :
        monitored.append(line)
    #----------------------------------------------------------------------
    # fill template
    #----------------------------------------------------------------------
    ELEMENTS  = string.join(elements,      "\n            ")
    CONTROL   = string.join(control_lines, "\n            ")
    MONITOR   = string.join(monitored,     "\n        ")
    filled_template = decida.interpolate(template)
    #----------------------------------------------------------------------
    # write output file
    #----------------------------------------------------------------------
    if os.path.isfile(output_file) :
        print "move or remove existing ", output_file
        exit()
    print "writing", output_file
    f = open(output_file, "w")
    for line in string.split(filled_template, "\n") :
        f.write(line + "\n")
    f.close()
    os.chmod(output_file, stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR)
