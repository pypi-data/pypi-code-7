################################################################################
# CLASS    : FormulaCalculator
# PURPOSE  : GUI for calculating simple formula
# AUTHOR   : Richard Booth
# DATE     : Sat Jun  2 11:55:18 EDT 2012
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
from Tkinter import *
import Tkinter
import string
from math import *
from decida.entry_emacs_bindings import *

class FormulaCalculator :
    """ Simple formula calculator. 

    **synopsis**:

    A small calculator can be useful to evaluate a single formula involving
    a few parameters/variables. This formula calculator class constructs
    a small calculator which evaluates the formula or its inverse with
    respect to a particular parameter, according to specified code
    for each result. (originally posted as a Tcl/Tk application on wiki.tcl.tk)

    **constructor arguments**:

        .. option:: parent (Tkinter handle) (default=None)

              handle of frame or other widget to pack plot in.
              if this is not specified, top-level is created.

        .. option:: par_specs (list of lists of parameter specifications)

              each list of parameter specifications is: parameter name,
              text to be displayed for the parameter label in the GUI,
              units, initial value, key of equation recalculation formula.

        .. option:: recalc_specs (list of lists of formula specifications)

              each list of recalculation specifications is: recalculation key,
              formula.

    **results**:

        * Sets up GUI for formula recalculation.

        * Changing and typing return in a parameter entry box re-evaluates
          the respective formula.

        * Emacs-style bindings switch between entry boxes:
          ^n and ^p  focus on next or previous entry windows, respectively

    **example** (from test_FormulaCalculator_1): ::

        from decida.FormulaCalculator import FormulaCalculator
        fc = FormulaCalculator(None,
            title="L-C oscillator",
            par_specs = [
                ["L",    "Inductance",  "pH", 1000.0, "f"],
                ["C",    "Capacitance", "pF",  25.00, "f"],
                ["freq", "Frequency",   "GHz",  1.00, "L"],
            ],
            recalc_specs = [
                ["f", "freq = 1e3/(2*pi*sqrt(L*C))"],
                ["L", "L    = 1e6/(C*pow(2*pi*freq, 2))"],
                ["C", "C    = 1e6/(L*pow(2*pi*freq, 2))"],
            ]
        )
    """
    def __init__(self, parent=None, par_specs=None, recalc_specs=None,
        title=""
    ) :
        self.title = title
        self.__parent = parent
        self.__Component = {}
        self.__pars = []
        self.__ParInfo = {}
        self.__Recalc  = {}
        for item in par_specs :
            par, text, unit, value, rkey = item
            self.__pars.append(par)
            self.__ParInfo[par] = (text, unit, value, rkey)
        for item in recalc_specs :
            rkey, code = item
            self.__Recalc[rkey] = code
        self.__gui()
    def __quit(self):
        top = self.__Component["top"]
        top.quit()
    def __gui(self) :
        #---------------------------------------------------------------------
        # toplevel
        #---------------------------------------------------------------------
        if self.__parent == None:
            if not Tkinter._default_root :
                root = Tk()
                root.wm_state("withdrawn")
            top = Toplevel()
        else :
            top = Toplevel()
        top.protocol('WM_DELETE_WINDOW', self.__quit)
        self.__Component["top"] = top
        #---------------------------------------------------------------------
        # basic frames
        #---------------------------------------------------------------------
        ftext = Frame(top, bd=2, relief=RAISED)
        ftext.pack(side=TOP, fill=BOTH, expand=True)
        fpars = Frame(top, bd=2, relief=RAISED)
        fpars.pack(side=TOP, fill=BOTH, expand=True)
        mtext = Message(ftext, justify=CENTER, text=self.title, aspect=800)
        mtext.pack(side=LEFT, fill=BOTH, expand=True)
        bquit = Button(ftext, text="Quit", command=self.__quit)
        bquit.pack(side=LEFT, padx=3, pady=3, expand=True, fill=X)
        self.__Component["text"] = mtext
        self.__Component["quit"] = bquit
        ftext["background"]="cadet blue"
        bquit["width"]=12
        bquit["relief"]=RAISED
        bquit["background"]="dark khaki"
        bquit["foreground"]="black"
        #---------------------------------------------------------------------
        # parameter entry
        #---------------------------------------------------------------------
        entries = []
        for par in self.__pars :
            text, unit, value, rkey = self.__ParInfo[par]
            fpar = Frame(fpars)
            fpar.pack(side=TOP, expand=True, fill=X)
            lpar = Label(fpar, text=text, width=30, anchor=W)
            lpar.pack(side=LEFT, expand=True, fill=X)
            epar = Entry(fpar, relief=SUNKEN, bd=2)
            epar.pack(side=LEFT, expand=True, fill=X)
            upar = Label(fpar, text=unit, width=15, anchor=CENTER)
            upar.pack(side=LEFT, expand=True, fill=X)
            self.__Component["%s-entry" % (par)] = epar
            epar.insert(0, value)
            def par_recalc(event, self=self, par=par) :
                self.recalculate(par)
            epar.bind("<Return>", par_recalc)
            lpar["background"] = "cadet blue"
            lpar["foreground"] = "white"
            upar["background"] = "cadet blue"
            upar["foreground"] = "white"
            epar["background"] = "GhostWhite"
            epar["foreground"] = "black"
            entries.append(epar)
        entry_emacs_bindings(entries)
        self.recalculate(self.__pars[0])
        #top.wait_visibility()
        #top.grab_set()
        top.mainloop()
        #top.destroy()
        #root = Tkinter._default_root
        #root.update()
    def recalculate(self, par_changed) :
        rkey = self.__ParInfo[par_changed][3]
        if rkey in self.__Recalc :
            for par in self.__pars :
                value = self.__Component["%s-entry" % (par)].get()
                exec("%s = %s" % (par, value))
            code = self.__Recalc[rkey]
            lines = string.split(code, "\n")
            for line in lines:
                line = string.strip(line)
                if len(line) == 0 : continue
                exec(line)
        for par in self.__pars :
            exec("par_value = %s" % (par))
            epar = self.__Component["%s-entry" % (par)]
            epar.delete(0, END)
            epar.insert(0, par_value)
