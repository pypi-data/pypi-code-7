################################################################################
# FUNCTION : tb
# PURPOSE  : read SmartSpice, Verilog netlist, generate new Verilog netlist
# AUTHOR   : Richard Booth
# DATE     : Sat Nov  9 11:25:30 2013
# -----------------------------------------------------------------------------
# NOTES    : 
#   * supply1_names, supply1_names used in test-bench generation
#   * pwr_ports used to generate place-and-route file
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
###############################################################################
import user
import decida
import string
import re
import os
import os.path
import shutil
import time

supply1_names = ("vdd", "v3p3")
supply0_names = ("gnd", "gnda", "agnd", "vss", "sub", "vsub")
pwr_ports = []
pwr_ports.extend(supply1_names)
pwr_ports.extend(supply0_names)
template = """\
//##########################################################################
// NAME    : $FILE
// PURPOSE : testbench for $CIRCUIT
// DATE    : $DATE
// AUTHOR  : $AUTHOR
//##########################################################################
!control .ext=all
`timescale 1ns / 1ps
`define TIMESCALE 1e-9
module $TESTBENCH();
    //----------------------------------------------------------------------
    // inputs
    //----------------------------------------------------------------------
$INPUTS
    //----------------------------------------------------------------------
    // outputs
    //----------------------------------------------------------------------
$OUTPUTS
    //----------------------------------------------------------------------
    // supply
    //----------------------------------------------------------------------
$SUPPLY1S
$SUPPLY0S
    //----------------------------------------------------------------------
    // resources
    //----------------------------------------------------------------------
    real    rtime, pi, freq;
    integer ifile;
    //----------------------------------------------------------------------
    // bit-blasted inputs/outputs
    //----------------------------------------------------------------------
$BBLAST
    //----------------------------------------------------------------------
    // DUT:
    //----------------------------------------------------------------------
$DUT
    //----------------------------------------------------------------------
    // clock
    //----------------------------------------------------------------------
    always begin
        #250 clk = ~clk;  // 2MHz
    end
    //----------------------------------------------------------------------
    // test sequence:
    //----------------------------------------------------------------------
    initial begin
        pi      = 3.1415926535;
        freq    = 1e5;
        clk     = 0;
$INPUT_INITS
        cdn     = 1;
        #10 cdn = 0;
        #10 cdn = 1;
        #1000000;
        $$stop;
    end
endmodule
"""

spj_template = """\
[Files]
0=$TB_FILE

[LibraryFiles]
0=.\\$TB_LIB\\{.v}
1=C:\\cygwin\\home\\$USER\\work\\1860bd18ba\\verilog_lib\\1860bd18ba_5v_ge5v_3rail.v
2=C:\\cygwin\\home\\$USER\\work\\1860bd18ba\\verilog_lib\\devices.v

[Options]
DebugEnable=Y

[Settings]
Version=Silvaco4.10.132.R
"""
#==========================================================================
# FUNCTION : verilog_compliant
# PURPOSE  : escape name if name is not compliant (to make it compliant!)
#==========================================================================
def verilog_compliant(name) :
    """ escape name if name is not compliant (to make it compliant!)."""
    m = re.search("^[a-zA-Z_][a-zA-Z_0-9]*$", name)
    if m:
        return name
    else:
        return "\%s " % (name)
#========================================================================
# FUNCTION : multiline
# PURPOSE  : split up line into multiple lines
#========================================================================
def multiline(line, linelength=72):
    """ split up line into multiple lines."""
    olines = []
    n = len(line)
    if n == 0 or n < linelength :
        olines.append(line)
    else :
        while n > linelength :
            found = False
            for i in range(linelength - 1, -1 , -1) :
                if line[i] in [" ", "\t"] :
                    found = True
                    break
            if  found :
                olines.append(line[0:i])
                line = line[i+1:]
            else :
                olines.append(line)
                line = ""
            n = len(line)
        if n > 0 :
            olines.append(line)
    return(olines)
#==========================================================================
# FUNCTION : tb
# PURPOSE  : read SmartSpice, Verilog netlist, generate new Verilog netlist
#==========================================================================
def tb(netlistdir, testbench, check=False, mod_dir=None):
    """ read SmartSpice, Verilog netlist, generate new Verilog netlist.

    use to generate a verilog test-bench.
    requires sspice netlist for correct bus notation.
    requires verilog for port directions.
    mod_dir has verilog files that overwrite modules in library.

    **arguments**:

        .. option::  netlistdir (string)

            directory where netlists \*.nes \*.v have been produced

        .. option:: testbench (string)

            netlist prefix

        .. option:: check (boolean) (optional, default=False)

            if True, produce check files for debugging

        .. option:: mod_dir (string) (optional, default=None)

            directory containing behavioral or modified modules to overwrite
            generated ones

    **procedure**: (% is a note specifically for the wrapper script)

        1. create a top-level schematic in Gateway

        2. simulation->create specific netlist:

             a. Type=SmartSpice, check "Make .SUBCKT",
                 change extension of netlist from .net to .nes
                 (to avoid overwriting non-subckt testbench for python script)

             b. Type=Verilog,
                 change extension of netlist from .net to .v

        3. edit wrapper script to point to the netlist directory and
           testbench prefix

        4. % if there are behavioral verilog modules that replace ones in the
           schematic, create a directory for them and point to it using the
           mod_dir parameter to the tb command

        5. % run the wrapper script

             a. creates a new directory with the name ${testbench}_lib, where
                testbench is the root of the verilog netlist name

             b. every module in the schematic comes out as a separate
                verilog module file in the \*_lib directory.

             c. if mod_lib was specified, files are copied from there to \*_lib
                and if replacing existing modules, the originals are copied to
                \*.orig

             d. the toplevel testbench is a module in \*_lib
                it is moved to the current directory and copied to \*.orig

        6. edit the toplevel testbench and put in head.x at the top of the file
           if available to include the testbench sequence, tasks, etc.

        7. start Silos and create or load existing project
           add libraries = \*_lib directory, standard-cell library
           add files = top-level testbench

        8. flush out all compilation errors

    """
    spice_testbench_netlist   = "%s/%s.nes" % (netlistdir, testbench)
    verilog_testbench_netlist = "%s/%s.v"   % (netlistdir, testbench)
    #----------------------------------------------------------------------
    # output file/directory:
    # root = os.path.splitext(os.path.basename(verilog_testbench_netlist))[0]
    #----------------------------------------------------------------------
    tb = string.lower(testbench)
    tb_lib      = "%s_lib"     % (tb)
    tb_lib_bak  = "%s_lib_bak" % (tb)
    tb_file     = "%s.v"       % (tb)
    tb_file_bak = "%s.v_bak"   % (tb)
    tb_spj      = "%s.spj"     % (tb)
    #----------------------------------------------------------------------
    # standard-cell database
    #----------------------------------------------------------------------
    devices = string.split("""
        res_pp1 cap_mim nmos5p0v pmos_5p0v
    """)
    stdcells = string.split("""
        v5_ad2d1 v5_ad2d2 v5_ad2d4
        v5_ad3d1 v5_ad3d2 v5_ad3d4
        v5_ad4d1 v5_ad4d2 v5_ad4d4
        v5_ant02
        v5_ao211d1 v5_ao211d2 v5_ao211d4
        v5_ao21d1 v5_ao21d2 v5_ao21d4
        v5_ao22d1 v5_ao22d2 v5_ao22d4
        v5_aoi211d1 v5_aoi211d2 v5_aoi211d4
        v5_aoi21d1 v5_aoi21d2 v5_aoi21d4
        v5_aoi222d1 v5_aoi222d2 v5_aoi222d4
        v5_aoi22d1 v5_aoi22d2 v5_aoi22d4
        v5_bshdr
        v5_dl200 v5_dl400 v5_dl600 v5_dl800
        v5_fd1d1 v5_fd1d2
        v5_fd1sd1 v5_fd1sd2
        v5_fd4d1 v5_fd4d2
        v5_fd4sd1 v5_fd4sd2
        v5_fdn1d1 v5_fdn1d2
        v5_fdn1sd1 v5_fdn1sd2
        v5_fdn4d1 v5_fdn4d2
        v5_fdn4sd1 v5_fdn4sd2
        v5_ivd1 v5_ivd12 v5_ivd2 v5_ivd3 v5_ivd4 v5_ivd6 v5_ivd8
        v5_ldn1d1 v5_ldn1d2 v5_ldn2d1 v5_ldn2d2
        v5_ldp1d1 v5_ldp1d2 v5_ldp2d1 v5_ldp2d2
        v5_mx2d1 v5_mx2d2 v5_mx2d4
        v5_mx4d1 v5_mx4d2 v5_mx4d4
        v5_nd2d1 v5_nd2d2 v5_nd2d4
        v5_nd3d1 v5_nd3d2 v5_nd3d4
        v5_nd4d1 v5_nd4d2 v5_nd4d4
        v5_nid1 v5_nid12 v5_nid2 v5_nid3 v5_nid4 v5_nid6 v5_nid8
        v5_nitd1 v5_nitd12 v5_nitd2 v5_nitd3 v5_nitd4 v5_nitd6 v5_nitd8
        v5_nr2d1 v5_nr2d2 v5_nr2d4
        v5_nr3d1 v5_nr3d2 v5_nr3d4
        v5_nr4d1 v5_nr4d2 v5_nr4d4
        v5_oa211d1 v5_oa211d2 v5_oa211d4
        v5_oa21d1 v5_oa21d2 v5_oa21d4
        v5_oa22d1 v5_oa22d2 v5_oa22d4
        v5_oai211d1 v5_oai211d2 v5_oai211d4
        v5_oai21d1 v5_oai21d2 v5_oai21d4
        v5_oai222d1 v5_oai222d2 v5_oai222d4
        v5_oai22d1 v5_oai22d2 v5_oai22d4
        v5_or2d1 v5_or2d2 v5_or2d4
        v5_or3d1 v5_or3d2 v5_or3d4
        v5_or4d1 v5_or4d2 v5_or4d4
        v5_tieh v5_tiel
        v5_xn2d1 v5_xn2d2 v5_xn2d4
        v5_xo2d1 v5_xo2d2 v5_xo2d4
    """)
    #----------------------------------------------------------------------
    # read spice netlist, eliminate continued lines and split into list
    # filter out comments
    # change <N> to __N
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
    lines = re.sub("<", "__", lines)
    lines = re.sub(">", "", lines)
    lines = string.lower(lines)
    llines = string.split(lines, "\n")
    spice_lines = []
    title = llines.pop(0)
    for line in llines :
        m = re.search("^ *\*", line)
        if m :
            continue
        line = re.sub("\$.*$", "", line)
        line = string.strip(line)
        if len(line) > 0 :
            spice_lines.append(line)
    #----------------------------------------------------------------------
    # read verilog netlist and split into list
    # filter out comments
    #----------------------------------------------------------------------
    if not os.path.isfile(verilog_testbench_netlist) :
        print "verilog testbench netlist \"%s\" is not readable" % \
            (verilog_testbench_netlist)
        exit()
    f = open(verilog_testbench_netlist, "r")
    lines = f.read()
    f.close()
    lines = re.sub("\r", " ", lines)
    lines = string.lower(lines)
    llines = string.split(lines, "\n")
    verilog_lines = []
    for line in llines :
        m = re.search("^ *//", line)
        if m :
            continue
        line = string.strip(line)
        if len(line) > 0 :
            verilog_lines.append(line)
    #----------------------------------------------------------------------
    # check 1:
    #----------------------------------------------------------------------
    if check:
        f = open("TBcheck.net", "w")
        f.write("* SPICE:\n")
        for line in spice_lines :
            f.write(line + "\n")
        f.close()
        f = open("TBcheck.v", "w")
        f.write("// VERILOG:\n")
        for line in verilog_lines :
            f.write(line + "\n")
        f.close()
    #----------------------------------------------------------------------
    # go through spice lines to gather module port lists (in spice order)
    # pandr ports = non-power ports
    #----------------------------------------------------------------------
    SubcktPorts={}
    Pandr_Ports={}
    subckts = []
    subckt = None
    for line in spice_lines :
        m = re.search("^.subckt ", line)
        if m :
            lline = string.split(line)
            lline.pop(0)
            subckt = lline.pop(0)
            subckts.append(subckt)
            SubcktPorts[subckt] = lline
            #--------------------------------------------------------------
            # non-verilog-compliant port names need to be escaped
            #--------------------------------------------------------------
            newports = []
            for port in SubcktPorts[subckt] :
                port = verilog_compliant(port)
                newports.append(port)
            SubcktPorts[subckt] = newports
            #--------------------------------------------------------------
            # end non-verilog-compliant port names
            #--------------------------------------------------------------
            #--------------------------------------------------------------
            # beg pandr
            #--------------------------------------------------------------
            Pandr_Ports[subckt] = []
            for port in SubcktPorts[subckt] :
                if not port in pwr_ports:
                    Pandr_Ports[subckt].append(port)
            #----------------------------------------------
            # verilog compliant already done on subcktports
            #----------------------------------------------
            #newports = []
            #for port in Pandr_Ports[subckt] :
            #    port = verilog_compliant(port)
            #    newports.append(port)
            #Pandr_Ports[subckt] = newports
            #--------------------------------------------------------------
            # end pandr
            #--------------------------------------------------------------
            continue
        m = re.search("^.ends ", line)
        if m :
            subckt = None
            continue
    #----------------------------------------------------------------------
    # get modules/subcircuits and port directions from verilog file
    #----------------------------------------------------------------------
    ModulePorts = {}
    modules = []
    module = None
    for line in verilog_lines :
        m = re.search("^module +([a-zA-Z_0-9]+)", line)
        if m :
            module = m.group(1)
            modules.append(module)
            Direction = {}
            continue
        m = re.search("^endmodule *$", line)
        if m :
            ModulePorts[module] = Direction
            module = None
            continue
        m = re.search("^(input|output|inout) +\[([0-9]+)\] *([^ ;]+) *;", line)
        if m :
            direction = m.group(1)
            bit  = string.atoi(m.group(2))
            port = m.group(3)
            port_bit = port + "__" + str(bit)
            port_bit = verilog_compliant(port_bit)
            Direction[port_bit] = direction
            continue
        m = re.search("^(input|output|inout) +\[([0-9]+):([0-9]+)\] *([a-zA-Z_0-9]+);", line)
        if m :
            direction = m.group(1)
            bus2 = string.atoi(m.group(2))
            bus1 = string.atoi(m.group(3))
            port = m.group(4)
            if bus1 > bus2 :
                bus1, bus2 = bus2, bus1
            for bit in range(bus1, bus2+1) :
                port_bit = port + "__" + str(bit)
                port_bit = verilog_compliant(port_bit)
                Direction[port_bit] = direction
            continue
        m = re.search("^(input|output|inout) +([^ ;]+) *;", line)
        if m :
            direction = m.group(1)
            port = m.group(2)
            port = verilog_compliant(port)
            Direction[port] = direction
            continue
    #----------------------------------------------------------------------
    # check 2:
    #----------------------------------------------------------------------
    if check:
        f = open("TBcheck.ports", "w")
        f.write("Verilog:\n")
        for module in modules :
            f.write("module %s\n" % (module))
            for port in ModulePorts[module] :
                f.write("    %-6s %-12s;\n" % (ModulePorts[module][port], port))
        f.write("Spice:\n")
        for subckt in subckts :
            f.write("subckt %s\n" % (subckt))
            for port in SubcktPorts[subckt] :
                f.write("    %-6s %-12s;\n" % ("inout", port))
        f.close()
    #----------------------------------------------------------------------
    # go through spice lines and generate testbench
    # plines = pandr lines
    #----------------------------------------------------------------------
    main_subckt = False
    vsrcs  = []
    olines = []
    plines = []
    skip = False
    for line in spice_lines :
        m = re.search("^.subckt", line)
        if m :
            lline = string.split(line)
            lline.pop(0)
            subckt = lline.pop(0)
            if subckt in stdcells :
                skip = True
                continue
            if subckt == string.lower(testbench) :
                main_subckt = True
            else :
                main_subckt = False
            #-----------------------------------------------------------------
            # beg non-pandr
            #-----------------------------------------------------------------
            olines.append("//" + "=" * 76)
            olines.append("//" + " module " + subckt)
            olines.append("//" + "=" * 76)
            subcktports = SubcktPorts[subckt]
            if len(subcktports) == 0:
                mline = "module %s();" % (subckt)
                olines.append(mline)
            else :
                mline = "module %s(" % (subckt)
                olines.append(mline)
                portlist = string.join(subcktports, ", ")
                mlines = multiline(portlist)
                for mline in mlines :
                    olines.append("    " + mline)
                olines.append(");")
            for port in subcktports :
                if not (port in ModulePorts[subckt]) :
                    print "Module Ports = ", ModulePorts[subckt]
                    print "(%s) spice port %s not in verilog ports" % (subckt, port)
                direction = ModulePorts[subckt][port]
                oline = "    %-6s %s;" % (direction, port)
                olines.append(oline)
            #-----------------------------------------------------------------
            # end non-pandr
            #-----------------------------------------------------------------
            #-----------------------------------------------------------------
            # beg pandr
            #-----------------------------------------------------------------
            pandr_ports = Pandr_Ports[subckt]
            if len(pandr_ports) == 0:
                mline = "module %s();" % (subckt)
                plines.append(mline)
            else :
                mline = "module %s(" % (subckt)
                plines.append(mline)
                portlist = string.join(pandr_ports, ", ")
                mlines = multiline(portlist)
                for mline in mlines :
                    plines.append("    " + mline)
                plines.append(");")
            for port in pandr_ports :
                if not port in ModulePorts[subckt] :
                    print "(PANDR)"
                    print "Module Ports = ", ModulePorts[subckt]
                    print "(%s) spice port %s not in verilog ports" % (subckt, port)
                direction = ModulePorts[subckt][port]
                pline = "    %-6s %s;" % (direction, port)
                plines.append(pline)
            #-----------------------------------------------------------------
            # end pandr
            #-----------------------------------------------------------------

        m = re.search("^.ends", line)
        if m :
            if skip :
                skip = False
            else :
                olines.append("endmodule")
                plines.append("endmodule")
            continue
        m = re.search("^v", line)
        if m :
            if not main_subckt :
                continue
            lline = string.split(line)
            if len(lline) >= 4 :
                vsrcs.append(lline[1])
        m = re.search("^r", line)
        if m :
            if skip :
                continue
            lline = string.split(line)
            if len(lline) == 4 :
                res, node1, node2, value = lline
            else :
                continue
            value = decida.spice_value(value)
            oline = "    res_veri %s(.p(%s), .n(%s));" % (res, node1, node2)
            olines.append(oline)
            plines.append(oline)
            continue
        m = re.search("^c", line)
        if m :
            if skip :
                continue
            lline = string.split(line)
            if len(lline) == 4 :
                cap, node1, node2, value = lline
            else :
                continue
            value = decida.spice_value(value)
            oline = "    cap_veri %s(.p(%s), .n(%s));" % (cap, node1, node2)
            olines.append(oline)
            plines.append(oline)
            continue
        m = re.search("^x", line)
        if m :
            if skip :
                continue
            line   = re.sub(" *= *", "=", line)
            lline  = string.split(line)
            inst   = lline.pop(0)
            instports  = []
            instparams = []
            isport = True
            for item in lline :
                if isport :
                    m = re.search("=", item)
                    if m :
                        isport = False
                        instparams.append(item)
                    else :
                        instports.append(item)
                else :
                    m = re.search("=", item)
                    if m :
                        instparams.append(item)
                    else :
                        print("ports follow params:", "  " + line)
            subckt = instports.pop(-1)
            if not subckt in SubcktPorts :
                # devices
                # print "skipping device: ", subckt
                continue
            subcktports = SubcktPorts[subckt]
            if subcktports == None:
                # instances of non-netlisted elements:
                print "skipping inst ", inst
                continue
            if len(subcktports) != len(instports):
                print("subckt=%s: instance ports don't match up with subckt" %
                    (subckt))
                print("  subckt  : %s" % (string.join(subcktports)))
                print("  instance: %s" % (string.join(instports)))
            #--------------------------------------------------------------
            # non-verilog-compliant port names need to be escaped
            #--------------------------------------------------------------
            newports = []
            for port in instports :
                port = verilog_compliant(port)
                newports.append(port)
            instports = newports
            #--------------------------------------------------------------
            # end non-verilog-compliant port names
            #--------------------------------------------------------------
            portlist = []
            for instport, subcktport in zip(instports, subcktports):
                portlist.append(".%s(%s)" % (subcktport, instport))
            portlist = string.join(portlist, ", ")
            iline = "%s %s(%s);" % (subckt, inst, portlist)
            ilines = multiline(iline)
            iline = ilines.pop(0)
            olines.append("    " + iline)
            for iline in ilines :
                olines.append("        " + iline)
            #--------------------------------------------------------------
            # beg pandr
            #--------------------------------------------------------------
            portlist = []
            for instport, subcktport in zip(instports, subcktports):
                if not subcktport in pwr_ports :
                    portlist.append(".%s(%s)" % (subcktport, instport))
            portlist = string.join(portlist, ", ")
            iline = "%s %s(%s);" % (subckt, inst, portlist)
            ilines = multiline(iline)
            iline = ilines.pop(0)
            plines.append("    " + iline)
            for iline in ilines :
                plines.append("        " + iline)
            #--------------------------------------------------------------
            # end pandr
            #--------------------------------------------------------------
    #----------------------------------------------------------------------
    # move existing testbench directory and testbench file out of the way
    #----------------------------------------------------------------------
    if os.path.isdir(tb_lib) :
        if os.path.isdir(tb_lib_bak) :
            print "removing existing backup tb dir \"%s\""  % (tb_lib_bak)
            shutil.rmtree(tb_lib_bak)
        print "moving existing testbench dir to \"%s\""     % (tb_lib_bak)
        shutil.move(tb_lib, tb_lib_bak)
    if os.path.isfile(tb_file) :
        if os.path.isfile(tb_file_bak) :
            print "removing existing backup tb file \"%s\"" % (tb_file_bak)
            os.remove(tb_file_bak)
        print "moving existing testbench file to \"%s\""    % (tb_file_bak)
        shutil.move(tb_file, tb_file_bak)
    #----------------------------------------------------------------------
    # write modules to separate files
    #----------------------------------------------------------------------
    cwd = os.getcwd()
    os.mkdir(tb_lib)
    os.chdir(tb_lib)
    f = None
    for oline in olines :
        m = re.search("^module +([a-zA_Z0-9_]+)", oline)
        if m :
            module = m.group(1)
            print "writing module", module
            f = open(module + ".v", "w")
            f.write(oline + "\n")
        elif re.search("^endmodule *$", oline) :
            if f :
                f.write(oline + "\n")
            f.close()
            f = None
        else :
            if f :
                f.write(oline + "\n")
    os.chdir(cwd)
    #----------------------------------------------------------------------
    # write modifications into library
    #----------------------------------------------------------------------
    if mod_dir :
        if not os.path.isdir(mod_dir) :
            print "modification directory \"%s\" does not exist" % (mod_dir)
        else :
            mod_files = os.listdir(mod_dir)
            lib_files = os.listdir(tb_lib)
            for file in mod_files:
                if file in lib_files :
                    shutil.move("%s/%s" % (tb_lib, file),
                                "%s/%s.orig" % (tb_lib, file))
                shutil.copy("%s/%s" % (mod_dir, file),
                            "%s/%s" % (tb_lib, file))
    #----------------------------------------------------------------------
    # generate testbench file in current directory
    #----------------------------------------------------------------------
    try :
        USER = os.environ["USERNAME"]
    except :
        USER = os.environ["USER"]
    AUTHOR    = USER
    TB_FILE   = tb_file
    TB_LIB    = tb_lib
    FILE      = tb_file
    DATE      = time.asctime(time.localtime(time.time()))
    TESTBENCH = testbench
    CIRCUIT   = testbench
    m = re.search("^(TEST_|TB_TEST|TB_|test_|tb_test|tb_)(.+)$", testbench)
    if m :
        CIRCUIT = m.group(2)
    OUTPUTS    = ""
    #----------------------------------------------------------------------
    # generate reg inputs
    #----------------------------------------------------------------------
    input_lines      = []
    input_init_lines = []
    supply1_lines    = []
    supply0_lines    = []
    bblast_lines     = []
    vsrcs.sort()
    buses = []
    Busbits = {}
    for vsrc in vsrcs :
        m = re.search("^(.+)__([0-9]+)", vsrc)
        if m :
            bus = m.group(1)
            bit = int(m.group(2))
            if not bus in buses :
                buses.append(bus)
                Busbits[bus] = []
            Busbits[bus].append(bit)
        else :
            if   vsrc in supply1_names :
                supply1_lines.append("    supply1 %s;" % (vsrc))
            elif vsrc in supply0_names :
                supply0_lines.append("    supply0 %s;" % (vsrc))
            else :
                input_lines.append("    reg  %s;" % (vsrc))
                input_init_lines.append("        %s = 0;" % (vsrc))
    for bus in buses :
        bits = Busbits[bus]
        bits.sort(reverse=True)
        msb = max(bits)
        lsb = min(bits)
        input_lines.append("    reg  [%d:%d] %s;" % (msb, lsb, bus))
        input_init_lines.append("        %s = %d'd0;" % (bus, msb-lsb+1))
        bb = []
        for bit in bits :
            bb.append("%s__%d" % (bus, bit))
        bb = string.join(bb, ", ")
        bblast_lines.append("    wire    %s;" % (bb))
        bblast_lines.append("    assign {%s} = %s;" % (bb, bus))
    INPUTS      = string.join(input_lines,   "\n")
    SUPPLY1S    = string.join(supply1_lines, "\n")
    SUPPLY0S    = string.join(supply0_lines, "\n")
    INPUT_INITS = string.join(input_init_lines, "\n")
    #----------------------------------------------------------------------
    # generate wire outputs
    #----------------------------------------------------------------------
    Direction = ModulePorts[string.lower(testbench)]
    ports = Direction.keys()
    ports.sort()
    output_lines = []
    buses = []
    Busbits = {}
    for port in ports :
        if Direction[port] == "output" :
            m = re.search("^(.+)__([0-9]+)", port)
            if m :
                bus = m.group(1)
                bit = int(m.group(2))
                if not bus in buses :
                    buses.append(bus)
                    Busbits[bus] = []
                Busbits[bus].append(bit)
            else :
                output_lines.append("    wire %s;" % (port))
    for bus in buses :
        bits = Busbits[bus]
        bits.sort(reverse=True)
        msb = max(bits)
        lsb = min(bits)
        output_lines.append("    wire [%d:%d] %s;" % (msb, lsb, bus))
        bb = []
        for bit in bits :
            bb.append("%s__%d" % (bus, bit))
        bb = string.join(bb, ", ")
        bblast_lines.append("    wire    %s;" % (bb))
        bblast_lines.append("    assign  %s = \n           {%s};" % (bus, bb))
    OUTPUTS  = string.join(output_lines,  "\n")
    BBLAST   = string.join(bblast_lines,  "\n")
    #----------------------------------------------------------------------
    # DUT variable for template
    #----------------------------------------------------------------------
    f = open("%s/%s" % (tb_lib, tb_file), "r")
    lines = f.read()
    f.close
    lines = re.sub("\r", " ", lines)
    lines = string.split(lines, "\n")
    dut_lines = []
    mode = False
    top  = False
    for line in lines :
        if   re.search("^ *module ",   line) :
            mode = True
            top  = True
            if re.search(";", line) :
                top = False
        elif re.search("^ *endmodule", line) :
            mode = False
        elif re.search("^ *(wire|input|output|ioput) ", line) :
            pass
        elif top :
            if re.search(";", line) :
                top = False
        elif mode :
            dut_lines.append(line)
    DUT = string.join(dut_lines, "\n")
    #----------------------------------------------------------------------
    # fill template
    #----------------------------------------------------------------------
    filled_template = decida.interpolate(template)
    #----------------------------------------------------------------------
    # write output file
    #----------------------------------------------------------------------
    print "writing", tb_file
    f = open(tb_file, "w")
    for line in string.split(filled_template, "\n") :
        f.write(line + "\n")
    f.close()
    shutil.copy(tb_file, tb_file + ".orig")
    #----------------------------------------------------------------------
    # fill project template if first go-around
    #----------------------------------------------------------------------
    if not os.path.isfile(tb_spj) :
        filled_template = decida.interpolate(spj_template)
        print "writing", tb_spj
        f = open(tb_spj, "w")
        for line in string.split(filled_template, "\n") :
            f.write(line + "\n")
        f.close()
    #======================================================================
    # write pandr file
    # filter out the test_bench module
    #======================================================================
    f = open("%s_pandr.v" % (CIRCUIT), "w")
    main_module = False
    for pline in plines :
        #---------------------------------------------
        # wanted to see if <0> is better than __0 (NO)
        #pline = re.sub("__([0-9]+)", "<\\1>", pline)
        #---------------------------------------------
        m = re.search("^ *module ([^(]+)",   pline)
        if m:
            module = m.group(1)
            if module == string.lower(testbench) :
                main_module = True
            else :
                main_module = False
        if not main_module :
            f.write("%s\n" % (pline))
        if re.search("^ *endmodule ",   pline) :
            main_module = False
    f.close
