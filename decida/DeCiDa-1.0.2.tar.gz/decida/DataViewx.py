################################################################################
# CLASS    : DataViewx
# PURPOSE  : editable data viewer
# AUTHOR   : Richard Booth
# DATE     : Sat Nov  9 11:19:43 2013
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
import sys
import os
import os.path
import string
import re
import numpy
import decida
import math
from decida.ItclObjectx      import ItclObjectx
from decida.FrameNotebook    import FrameNotebook
from decida.TextWindow       import TextWindow
from decida.Data             import Data
from decida.Calc             import Calc
from decida.XYplotx          import XYplotx
from decida.Histogramx       import Histogramx
from decida.SelectionDialog  import SelectionDialog
from decida.EquationParser   import EquationParser
from decida.MessageDialog    import MessageDialog
import Tkinter
from Tkinter import *
import tkFileDialog
import tkMessageBox

class DataViewx(ItclObjectx, Frame) :
    """ read, view, manipulate and write data.

    *DataViewx* is used to read data in various formats and provide X and Y
    columns to plot the data using *XYplotx*.  Any column in the data set
    can be plotted versus any other column.  *DataViewx* provides many 
    data-editing tools, such as data-removal, column operations on the data
    set, FFT, filtering, and reordering.

    The DeCiDa *dataview* application instantiates a *DataViewx* object if
    only one data-file is to be read (otherwise, it uses *XYplotx* to 
    display data from two or more files).

    **constructor arguments** :
        .. option:: parent (Tkinter handle)
        
            handle of frame or other widget to pack plot in.
            if this is not specified, top-level is created.

        .. option:: \*\*kwargs (dict)

            options or configuration-options

    **options**:

        .. option::  data (data pointer)

            data object to view

        .. option::  command (list)

            *not yet implemented*

    **configuration options**:

        .. option::  verbose (boolean) (default=False)

            enable/disable verbose mode

        .. option::  title (string) (default="")

            specify plot height

        .. option::  plot_width (string) (default="6i")

            specify plot width

        .. option::  plot_height (string) (default="6i")

            specify plot height

        .. option::  wait (boolean) (optional, default=False)

            wait in main-loop until window is destroyed

        .. option:: destroy (boolean) (optional, default=False)

            destroy main window after it has been displayed.
            useful for displaying, generating PostScript, then
            destroying window.

    **example** (from test_DataViewx_2): ::

        from decida.Data import Data
        from decida.DataViewx import DataViewx
        
        d = Data()
        d.read("LTspice_ac_binary.raw")
        DataViewx(data=d, command=[["frequency DB(V(vout1)) PH(V(vout1))", "xaxis=\"log\""]])

    **public methods**:

        * public methods from *ItclObjectx*

    """
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # DataViewx main
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD  : __init__
    # PURPOSE : constructor
    #==========================================================================
    def __init__(self, parent=None, **kwargs) :
        ItclObjectx.__init__(self)
        #----------------------------------------------------------------------
        # private variables:
        #----------------------------------------------------------------------
        self.__parent = parent
        self.__Component = {}
        self.__Plot   = {}
        self.__table_names = []
        self.__command = None
        #----------------------------------------------------------------------
        # configuration options:
        #----------------------------------------------------------------------
        if sys.platform == "darwin" :
            plot_width  = "8i"
            plot_height = "8i"
        else :
            plot_width  = "6i"
            plot_height = "6i"
        self._add_options({
            "verbose"      : [False, None],
            "title"        : ["", None],
            "plot_width"   : [plot_width, None],
            "plot_height"  : [plot_height, None],
            "wait"         : [True, None],
            "destroy"      : [False, None],
        })
        #----------------------------------------------------------------------
        # keyword arguments are *not* all configuration options
        #----------------------------------------------------------------------
        for key, value in kwargs.items() :
            if   key == "data" :
                self.__data_obj_orig = value
                self.__data_obj = self.__data_obj_orig.dup()
                self.__data_obj.edit()
                self.__data_obj.set("point = index")
            elif key == "command" :
                self.__command = value
            else :
                self[key] = value
        #----------------------------------------------------------------------
        # build gui:
        #----------------------------------------------------------------------
        self.__gui()
    #===========================================================================
    # METHOD  : __del__
    # PURPOSE : destructor
    #===========================================================================
    def __del__(self) :
        if self.__toplevel :
            self.__toplevel.destroy()
        else :
            self.destroy()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # DataViewx configuration option callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # DataViewx GUI
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD  : __gui
    # PURPOSE : build graphical user interface
    #==========================================================================
    def __gui(self) :
        #---------------------------------------------------------------------
        # top-level:
        #---------------------------------------------------------------------
        if self.__parent == None:
            if not Tkinter._default_root :
                root = Tk()
                root.wm_state("withdrawn")
            self.__toplevel = Toplevel()
            self.__toplevel.wm_state("withdrawn")
            Frame.__init__(self, self.__toplevel, class_ = "DataViewx")
            if not self.was_configured("wait") :
                self["wait"] = True
        else:
            self.__toplevel = None
            Frame.__init__(self, self.__parent,   class_ = "DataViewx")
            if not self.was_configured("wait") :
                self["wait"] = False
        self.pack(side=TOP, fill=BOTH, expand=True)
        #---------------------------------------------------------------------
        # option database:
        #---------------------------------------------------------------------
        if sys.platform == "darwin" :
            self.option_add("*DataViewx*Menubutton.width", 12)
            self.option_add("*DataViewx*Menubutton.height", 1)
            self.option_add("*DataViewx*Menubutton.bd", 2)
            self.option_add("*DataViewx*Menubutton.relief", RAISED)
            self.option_add("*DataViewx*Label.width", 10)
            self.option_add("*DataViewx*Label.anchor", E)
            self.option_add("*DataViewx*Label.relief", SUNKEN)
            self.option_add("*DataViewx*Label.bd", 2)
            self.option_add("*DataViewx*Entry.width", 15)
            self.option_add("*DataViewx*Checkbutton.width", 12)
            self.option_add("*DataViewx*Checkbutton.anchor", W)
            self.option_add("*DataViewx*Checkbutton.bd", 2)
            self.option_add("*DataViewx*Checkbutton.relief", RAISED)
            self.option_add("*DataViewx*Checkbutton.highlightThickness", 0)
            #elf.option_add("*DataViewx*Checkbutton.background", "rosy brown")
            self.option_add("*DataViewx*Radiobutton.anchor", W)
            self.option_add("*DataViewx*Radiobutton.highlightThickness", 0)
            self.option_add("*DataViewx*Button.highlightThickness", 0)
            self.option_add("*DataViewx*Button.width", 10)
            self.option_add("*DataViewx*Button.height", 1)
            self.option_add("*DataViewx*Entry.font", "Courier 20 bold")
        else :
            self.option_add("*DataViewx*Menubutton.width", 12)
            self.option_add("*DataViewx*Menubutton.height", 1)
            self.option_add("*DataViewx*Menubutton.bd", 2)
            self.option_add("*DataViewx*Menubutton.relief", RAISED)
            self.option_add("*DataViewx*Label.width", 10)
            self.option_add("*DataViewx*Label.anchor", E)
            self.option_add("*DataViewx*Label.relief", SUNKEN)
            self.option_add("*DataViewx*Label.bd", 2)
            self.option_add("*DataViewx*Entry.width", 20)
            self.option_add("*DataViewx*Checkbutton.width", 12)
            self.option_add("*DataViewx*Checkbutton.anchor", W)
            self.option_add("*DataViewx*Checkbutton.bd", 2)
            self.option_add("*DataViewx*Checkbutton.relief", RAISED)
            self.option_add("*DataViewx*Checkbutton.highlightThickness", 0)
            #elf.option_add("*DataViewx*Checkbutton.background", "rosy brown")
            self.option_add("*DataViewx*Radiobutton.anchor", W)
            self.option_add("*DataViewx*Radiobutton.highlightThickness", 0)
            self.option_add("*DataViewx*Button.highlightThickness", 0)
            self.option_add("*DataViewx*Button.width", 10)
            self.option_add("*DataViewx*Button.height", 1)
            self.option_add("*DataViewx*Entry.font", "Courier 12 bold")
        #---------------------------------------------------------------------
        # main layout
        #---------------------------------------------------------------------
        mbar = Frame(self, relief=SUNKEN, bd=2)
        mbar.pack(side=TOP,   expand=False, fill=X, padx=2, pady=2)
        cols = Frame(self, relief=SUNKEN, bd=2)
        cols.pack(side=LEFT,  expand=False, fill=Y, padx=2, pady=2)

        yscr = Scrollbar(cols)
        yscr.pack(side=RIGHT, expand=False, fill=Y, padx=2, pady=2)
        canv = Canvas(cols)
        canv.pack(side=LEFT,  expand=True, fill=BOTH, padx=2, pady=2)

        table = Frame(canv, relief=SUNKEN, bd=2)
        table.pack(side=TOP,  expand=True, fill=BOTH, padx=10, pady=10)
        yscr.set(0, 0)
        yscr["command"] = canv.yview
        canv["yscrollcommand"] = yscr.set

        xtable = Frame(table, relief=SUNKEN, bd=2)
        xtable.pack(side=LEFT, fill=Y, padx=2, pady=2)
        ytable = Frame(table, relief=SUNKEN, bd=2)
        ytable.pack(side=LEFT, fill=Y, padx=2, pady=2)

        hubb = Frame(self, relief=SUNKEN, bd=2)
        hubb.pack(side=LEFT, expand=True, fill=BOTH, padx=2, pady=2)
        plot = Frame(hubb, relief=SUNKEN, bd=2)
        plot.pack(side=TOP, expand=True, fill=BOTH)
        book = FrameNotebook(plot, tab_location="right", header=False)

        mbar["background"]   = "steel blue"
        cols["background"]   = "steel blue"
        canv["background"]   = "steel blue"
        table["background"]  = "steel blue"
        xtable["background"] = "steel blue"
        ytable["background"] = "steel blue"
        hubb["background"]   = "steel blue"

        self.__Component["yscr"] = yscr
        self.__Component["canv"] = canv
        self.__Component["book"] = book
        self.__Component["table"] = table
        self.__Component["xtable"] = xtable
        self.__Component["ytable"] = ytable
        #---------------------------------------------------------------------
        # menu-bar
        #---------------------------------------------------------------------
        file_mb = Menubutton(mbar, text="File")
        file_mb.pack(side=LEFT, padx=5, pady=5)
        anal_mb = Menubutton(mbar, text="Analysis")
        anal_mb.pack(side=LEFT, padx=5, pady=5)
        oper_mb = Menubutton(mbar, text="Operations")
        oper_mb.pack(side=LEFT, padx=5, pady=5)
        help_bt = Button(mbar, text="Help")
        help_bt.pack(side=RIGHT, padx=5, pady=5)
        calc_bt = Button(mbar, text="Calculator")
        calc_bt.pack(side=RIGHT, padx=5, pady=5)
        dele_bt = Button(mbar, text="Delete")
        dele_bt.pack(side=RIGHT, padx=5, pady=5)
        next_bt = Button(mbar, text="Next")
        next_bt.pack(side=RIGHT, padx=5, pady=5)
        stak_bt = Button(mbar, text="Stack")
        stak_bt.pack(side=RIGHT, padx=5, pady=5)
        over_bt = Button(mbar, text="Overlay")
        over_bt.pack(side=RIGHT, padx=5, pady=5)
        star_bt = Button(mbar, text="Start")
        star_bt.pack(side=RIGHT, padx=5, pady=5)
        file_menu=Menu(file_mb)
        anal_menu=Menu(anal_mb)
        oper_menu=Menu(oper_mb)
        file_mb["menu"] = file_menu
        anal_mb["menu"] = anal_menu
        oper_mb["menu"] = oper_menu
        calc_bt["background"] = "green"
        calc_bt["foreground"] = "black"
        def calc_cmd() :
            calc_obj = Calc(wait=False)
        calc_bt["command"]    = calc_cmd
        help_bt["background"] = "powder blue"
        help_bt["foreground"] = "black"
        help_bt["command"]    = self.__help_cmd
        dele_bt["background"] = "red"
        dele_bt["foreground"] = "black"
        next_bt["background"] = "red"
        next_bt["foreground"] = "black"
        stak_bt["background"] = "red"
        stak_bt["foreground"] = "black"
        over_bt["background"] = "red"
        over_bt["foreground"] = "black"
        star_bt["background"] = "red"
        star_bt["foreground"] = "black"
        mblist = [file_mb, anal_mb, oper_mb, calc_bt, help_bt, dele_bt,
            next_bt, stak_bt, over_bt, star_bt]
        #tk_menuBar(mblist)
        #---------------------------------------------------------------------
        # button commands
        #---------------------------------------------------------------------
        def star_cmd(self=self) :
            self.__add_start()
        def over_cmd(self=self) :
            self.__add_overlay()
        def stak_cmd(self=self) :
            self.__add_stack()
        def next_cmd(self=self) :
            self.__add_next()
        def dele_cmd(self=self) :
            self.__del()
        star_bt["command"] = star_cmd
        over_bt["command"] = over_cmd
        stak_bt["command"] = stak_cmd
        next_bt["command"] = next_cmd
        dele_bt["command"] = dele_cmd
        #---------------------------------------------------------------------
        # file menu
        #---------------------------------------------------------------------
        file_menu.add_command(
            label="Read Data File",
            command=self.__read_file)
        file_menu.add_separator()
        file_menu.add_command(
            label="Accept data",
            state=DISABLED,
            command=self.__accept_data)
        file_menu.add_command(
            label="Restore data",
            state=DISABLED,
            command=self.__restore_data)
        file_menu.add_separator()
        file_menu.add_command(
            label="Write column format",
            command=self.__write_ssv)
        file_menu.add_command(
            label="Write comma-separated-value (csv) format",
            command=self.__write_csv)
        file_menu.add_command(
            label="Write piece-wise-linear (pwl) format",
            command=self.__write_pwl)
        file_menu.add_separator()
        file_menu.add_command(
            label="Reorder data",
            command=self.__reorder)
        file_menu.add_command(
            label="TextWindow",
            command=self.__textwindow)
        file_menu.add_separator()
        file_menu.add_command(
            label="Overlay All",
            command=self.__overlay_all)
        file_menu.add_separator()
        file_menu.add_command(
            label="Close Window",
            command=self.__close_cmd)
        file_menu.add_command(
            label="Exit DeCiDa",
            command=self.__exit_cmd)
        self.__Component["file_menu"] = file_menu
        #---------------------------------------------------------------------
        # analysis menu
        #---------------------------------------------------------------------
        anal_menu.add_command(
            label="Statistics",
            command=self.__stats)
        anal_menu.add_command(
            label="Frequency/Duty-cycle",
            command=self.__duty)
        anal_menu.add_command(
            label="Edges: Rise/Fall/Slew",
            command=self.__edges)
        anal_menu.add_command(
            label="Periodic Time-Average",
            command=self.__period_time_average)
        anal_menu.add_command(
            label="FFT",
            command=self.__fft)
        anal_menu.add_command(
            label="Jitter",
            command=self.__jitter)
        anal_menu.add_command(
            label="INL/DNL",
            command=self.__inl_dnl)
        #anal_menu.add_command(
        #    label="Time-Constant",
        #    command=self.__time_constant)
        #anal_menu.add_command(
        #    label="Step-Response",
        #    command=self.__step_response)
        anal_menu.add_command(
            label="Eye-Diagram",
            command=self.__eye_diagram)
        anal_menu.add_command(
            label="Oscilloscope",
            command=self.__scope_diagram)
        anal_menu.add_command(
            label="Low-Pass Filter",
            command=self.__filter)
        anal_menu.add_command(
            label="Moving Average Filter",
            command=self.__mavg_filter)
        anal_menu.add_command(
            label="Linear Regression",
            command=self.__linreg)
        anal_menu.add_command(
            label="Quadradic Regression",
            command=self.__quadreg)
        anal_menu.add_command(
            label="Fourier Expansion",
            command=self.__four)
        anal_menu.add_command(
            label="Histogram",
            command=self.__histogram)
        anal_menu.add_command(
            label="generate WAV file",
            command=self.__WAV)
        #---------------------------------------------------------------------
        # operations menu
        #---------------------------------------------------------------------
        oper_menu.add_command(
            label="Equation-Set",
            command=self.__colops)
        oper_menu.add_command(
            label="Analog to Digital",
            command=self.__a2d)
        oper_menu.add_command(
            label="Add delineator",
            command=self.__delineator)
        oper_menu.add_separator()
        oper_menu.add_command(
            label="-x",
            command=self.__neg_x)
        oper_menu.add_command(
            label="-y",
            command=self.__neg_y)
        oper_menu.add_command(
            label="abs(x)",
            command=self.__abs_x)
        oper_menu.add_command(
            label="abs(y)",
            command=self.__abs_y)
        oper_menu.add_command(
            label="1/y",
            command=self.__inv_y)
        oper_menu.add_command(
            label="delta(x)",
            command=self.__delta_x)
        oper_menu.add_command(
            label="dy/dx",
            command=self.__deriv_y_x)
        oper_menu.add_command(
            label="integ(y dx)",
            command=self.__integ_y_x)
        #---------------------------------------------------------------------
        # init
        #---------------------------------------------------------------------
        self.__xcol_Var = StringVar()
        self.__ycol_Var = StringVar()
        columns = self.__data_obj.names()
        for col in columns :
            self.__table_names.append(col)
            rb = Radiobutton(xtable, text=col, anchor=W, width=30,
                variable= self.__xcol_Var, value=col)
            rb.pack(side=TOP, fill=X)
            rb.bind("<MouseWheel>", self.__mouse_wheel)
            rb.bind("<Button-4>",   self.__mouse_wheel)
            rb.bind("<Button-5>",   self.__mouse_wheel)
            rb.bind("<Prior>",      self.__page_key)
            rb.bind("<Next>",       self.__page_key)
            rb.bind("<Home>",       self.__page_key)
            rb.bind("<End>",        self.__page_key)
            rb = Radiobutton(ytable, text=col, anchor=W, width=30,
                variable= self.__ycol_Var, value=col)
            rb.pack(side=TOP, fill=X)
            rb.bind("<MouseWheel>", self.__mouse_wheel)
            rb.bind("<Button-4>",   self.__mouse_wheel)
            rb.bind("<Button-5>",   self.__mouse_wheel)
            rb.bind("<Prior>",      self.__page_key)
            rb.bind("<Next>",       self.__page_key)
            rb.bind("<Home>",       self.__page_key)
            rb.bind("<End>",        self.__page_key)
        self.__xcol_Var.set(columns[0])
        self.__ycol_Var.set(columns[1])
        self.after_idle(self.__place_table)
        #---------------------------------------------------------------------
        # process command or add first plot
        #---------------------------------------------------------------------
        if not self.__command is None :
            start = True
            for plot in self.__command :
                cols = string.split(plot[0])
                args = None
                if len(plot) == 2 :
                    args = plot[1]
                xcol  = cols[0]
                ycols = cols[1:]
                ymode = "-overlay"
                for ycol in ycols :
                    if ycol in ("-stack", "-overlay", "-next") :
                        ymode = ycol
                    else :
                        self.__xcol_Var.set(xcol)
                        self.__ycol_Var.set(ycol)
                        if start :
                            self.__add_next(args)
                            start = False
                        else :
                            if   ymode == "-overlay" :
                                self.__add_overlay()
                            elif ymode == "-stack" :
                                self.__add_stack()
                            elif ymode == "-next" :
                                self.__add_next(args)
        else :
            self.__add_next()
        #---------------------------------------------------------------------
        # update / mainloop
        #---------------------------------------------------------------------
        self.update()
        if self.__toplevel :
            self.__toplevel.geometry("+20+20")
            self.__toplevel.wm_state("normal")
            self.__toplevel.wm_title(self["title"])
        if self["wait"] :
            self.wait_window()
        if self["destroy"] :
            if self.__toplevel :
                 self.__toplevel.destroy()
            else :
                 self.destroy()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # DataViewx user commands:
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD  : current_plot
    # PURPOSE : return current plot handle
    #==========================================================================
    def current_plot(self) :
        """ return the current plot handle. """
        book = self.__Component["book"]
        tabid = book.current_tab()
        if tabid is None : return None
        return self.__Plot[tabid]
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # DataViewx GUI construction methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #--------------------------------------------------------------------------
    # METHOD: __place_table :
    # PURPOSE: place table on scrollable canvas when ready
    #--------------------------------------------------------------------------
    def __place_table(self) :
        canv  = self.__Component["canv"]
        table = self.__Component["table"]
        book  = self.__Component["book"]
        canv.create_window(0, 0, anchor=NW, window=table)
        self.update_idletasks()
        width  = table.winfo_reqwidth()
        height = book.winfo_reqheight()
        #eight = min(height, self.winfo_pixels("8i"))
        canv["height"] = height
        canv["width"]  = width
        canv["scrollregion"] = canv.bbox(ALL)
        canv["yscrollincrement"] = "0.1i"
        def cmd(event, self=self) :
            self.update()
            yscr = self.__Component["yscr"]
            units = yscr.get()
            fill  = units[1] - units[0]
            yscr["width"] = "0.15i" if fill < 1  else 0
        self.bind("<Configure>", cmd)
    #--------------------------------------------------------------------------
    # METHOD: __adjust_table :
    # PURPOSE: adjust table after adding a new column entry
    #--------------------------------------------------------------------------
    def __adjust_table(self) :
        self.update_idletasks()
        canv  = self.__Component["canv"]
        canv["scrollregion"] = canv.bbox(ALL)
    #-------------------------------------------------------------------------
    # METHOD: __mouse_wheel
    # PURPOSE: mouse wheel events
    #-------------------------------------------------------------------------
    def __mouse_wheel(self, event) :
        canv  = self.__Component["canv"]
        yscr  = self.__Component["yscr"]
        if yscr["width"] != "0":
            if   (event.num == 4 or event.delta > 0) :
                canv.yview_scroll(-1, "units")
            elif (event.num == 5 or event.delta < 0) :
                canv.yview_scroll( 1, "units")
    #-------------------------------------------------------------------------
    # METHOD: __page_key
    # PURPOSE: canvas paging
    #-------------------------------------------------------------------------
    def __page_key(self, event) :
        canv  = self.__Component["canv"]
        yscr  = self.__Component["yscr"]
        if yscr["width"] != "0":
            if   (event.keysym == "Prior") :
                canv.yview_scroll(-1, "pages")
            elif (event.keysym == "Next") :
                canv.yview_scroll( 1, "pages")
            elif (event.keysym == "Home") :
                canv.yview_moveto(0)
            elif (event.keysym == "End") :
                canv.yview_moveto(1)
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # DataViewx GUI file menu callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #--------------------------------------------------------------------------
    # METHOD  : __exit_cmd
    # PURPOSE : exit file menu callback
    #--------------------------------------------------------------------------
    def __exit_cmd(self) :
        self.__close_cmd()
        os._exit(0)
    #--------------------------------------------------------------------------
    # METHOD  : __close_cmd
    # PURPOSE : close file menu callback
    #--------------------------------------------------------------------------
    def __close_cmd(self) :
        self.quit()
        if self.__toplevel :
             self.__toplevel.destroy()
        else :
             self.destroy()
    #--------------------------------------------------------------------------
    # METHOD  : __reorder
    # PURPOSE : reorder data
    #--------------------------------------------------------------------------
    def __reorder(self) :
        dobj = self.__data_obj
        #----------------------------------------------------------------------
        # reorder dialog
        #----------------------------------------------------------------------
        guispecs = [
            ["entry", "reorder columns",  [
                 ["columns", "column list",  ""],
            ]],
        ]
        sd = SelectionDialog(self, title="Reorder columns", guispecs=guispecs)
        V = sd.go()
        if V["ACCEPT"] :
            cols = string.split(V["columns"])
            dobj_cols = dobj.names()
            ok = True
            for col in cols :
                if not col in dobj_cols :
                    ok = False
            if ok:
                dobj.sort(cols)
                dobj.set_parsed("point = index")
                self.__data_modified()
    #--------------------------------------------------------------------------
    # METHOD  : __textwindow
    # PURPOSE : text window data
    #--------------------------------------------------------------------------
    def __textwindow(self) :
        dobj = self.__data_obj
        dobj.twin()
    #--------------------------------------------------------------------------
    # METHOD  : __read_file
    # PURPOSE : read data file
    #--------------------------------------------------------------------------
    def __read_file(self, file=None) :
        if not file :
            file = tkFileDialog.askopenfilename(
                parent = self,
                title = "data file name to read?",
                initialdir = os.getcwd(),
                filetypes = (
                    ("data files", "*.col"),
                    ("data files", "*.ssv"),
                    ("data files", "*.csv"),
                    ("data files", "*.tsv"),
                    ("data files", "*.raw"),
                    ("data files", "*.csdf"),
                    ("data files", "*.tr0"),
                    ("data files", "*.ac0"),
                    ("all files", "*")
                )
            )
        if not file:
            return
        elif not os.path.isfile(file):
            print "file " + file + " doesn't exist"
            return
        dobj = Data()
        # file/format dialog?
        dobj.read(file)
        self.__data_obj_orig = dobj
        self.__data_obj = self.__data_obj_orig.dup()
        self.__data_obj.edit()
        self["title"] = file
        self.__command = None
        self.__gui()
    #--------------------------------------------------------------------------
    # METHOD  : __data_modified
    # PURPOSE : when data set is modified, enable File->restore/accept
    #--------------------------------------------------------------------------
    def __data_modified(self) :
        fm = self.__Component["file_menu"]
        ja = fm.index("Accept data")
        jr = fm.index("Restore data")
        fm.entryconfigure(ja, state=NORMAL)
        fm.entryconfigure(jr, state=NORMAL)
    #--------------------------------------------------------------------------
    # METHOD  : __data_unmodified
    # PURPOSE : when data set is read-in, disable File->restore/accept
    #--------------------------------------------------------------------------
    def __data_unmodified(self) :
        fm = self.__Component["file_menu"]
        ja = fm.index("Accept data")
        jr = fm.index("Restore data")
        fm.entryconfigure(ja, state=DISABLED)
        fm.entryconfigure(jr, state=DISABLED)
    #--------------------------------------------------------------------------
    # METHOD  : __accept_data
    # PURPOSE : copy working data back to original data
    #--------------------------------------------------------------------------
    def __accept_data(self) :
        self.__data_obj_orig = self.__data_obj.dup()
        self.__data_unmodified()
    #--------------------------------------------------------------------------
    # METHOD  : __restore_data
    # PURPOSE : copy original data back to working data
    #--------------------------------------------------------------------------
    def __restore_data(self) :
        self.__data_obj = self.__data_obj_orig.dup()
        self.__data_unmodified()
        #----------------------------------------------------------------------
        # re-create point column
        #----------------------------------------------------------------------
        self.__data_obj.set("point = index")
        #----------------------------------------------------------------------
        # remove table columns if not in original data
        #----------------------------------------------------------------------
        table_names = self.__table_names
        data_names  = self.__data_obj.names()
        for name in table_names :
            if not name in data_names :
                self.__del_data_col(name)
        #----------------------------------------------------------------------
        # repaint current plot
        #----------------------------------------------------------------------
        dobj   = self.__data_obj
        xy     = self.current_plot()
        if xy is None : return
        curves = xy.curves()
        cc     = xy.current_curve()
        for curve in curves :
            A = xy.curve_attributes(curve)
            xcol = A["xname"]
            ycol = A["yname"]
            if xcol in data_names and ycol in data_names :
                xy.delete_curve(curve, redraw=False)
                xy.add_curve(dobj, xcol, ycol,
                    autoscale_x=False, autoscale_y=False,
                    lstate=A["lstate"], sstate=A["sstate"],
                    color=A["color"], symbol=A["symbol"], ssize=A["ssize"],
                    wline=A["wline"], trace=A["trace"])
        xy.current_curve(cc)
    #--------------------------------------------------------------------------
    # METHOD  : __write_ssv
    # PURPOSE : write data file
    # NOTES : 
    #    * TBD: file/format dialog?
    #--------------------------------------------------------------------------
    def __write_ssv(self, file=None) :
        if not file :
            file = tkFileDialog.asksaveasfilename(
                parent = self,
                title = "(space-separated value format) data file name to save?",
                initialdir = os.getcwd(),
                defaultextension = ".col",
                filetypes = (
                    ("column format files", "*.col"),
                    ("column format files", "*.ssv"),
                    ("data files", "*.pwl"),
                    ("data files", "*.col"),
                    ("data files", "*.ssv"),
                    ("data files", "*.csv"),
                    ("data files", "*.tsv"),
                    ("data files", "*.raw"),
                    ("data files", "*.csdf"),
                    ("data files", "*.tr0"),
                    ("data files", "*.ac0"),
                    ("all files", "*")
                )
            )
        if not file:
            return
        self.__data_obj.write_ssv(file)
    #--------------------------------------------------------------------------
    # METHOD  : __write_csv
    # PURPOSE : write data file
    # NOTES : 
    #    * TBD: file/format dialog?  then make one write proc
    #--------------------------------------------------------------------------
    def __write_csv(self, file=None) :
        if not file :
            file = tkFileDialog.asksaveasfilename(
                parent = self,
                title = "(comma-separated value format) data file name to save?",
                initialdir = os.getcwd(),
                defaultextension = ".csv",
                filetypes = (
                    ("CSV files", "*.csv"),
                    ("data files", "*.pwl"),
                    ("data files", "*.col"),
                    ("data files", "*.ssv"),
                    ("data files", "*.csv"),
                    ("data files", "*.tsv"),
                    ("data files", "*.raw"),
                    ("data files", "*.csdf"),
                    ("data files", "*.tr0"),
                    ("data files", "*.ac0"),
                    ("all files", "*")
                )
            )
        if not file:
            return
        self.__data_obj.write_csv(file)
    #--------------------------------------------------------------------------
    # METHOD  : __write_pwl
    # PURPOSE : write piece-wise-linear file
    # NOTES : 
    #    * TBD: file/format dialog?  then make one write proc
    #--------------------------------------------------------------------------
    def __write_pwl(self, file=None) :
        if not file :
            file = tkFileDialog.asksaveasfilename(
                parent = self,
                title = "(piece-wise linear format) data file name to save?",
                initialdir = os.getcwd(),
                defaultextension = ".pwl",
                filetypes = (
                    ("PWL files", "*.pwl"),
                    ("data files", "*.pwl"),
                    ("data files", "*.col"),
                    ("data files", "*.ssv"),
                    ("data files", "*.csv"),
                    ("data files", "*.tsv"),
                    ("data files", "*.raw"),
                    ("data files", "*.csdf"),
                    ("data files", "*.tr0"),
                    ("data files", "*.ac0"),
                    ("all files", "*")
                )
            )
        if not file:
            return
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        dobj.write_pwl(file, xcol, ycol)
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # DataViewx GUI analysis menu callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD  : __stats
    # PURPOSE : analysis -> stats
    #==========================================================================
    def __stats(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # calculate stats
        #----------------------------------------------------------------------
        yrms = dobj.rms(xcol, ycol)
        yavg = dobj.time_average(xcol, ycol)
        ymin = dobj.min(ycol)
        ymax = dobj.max(ycol)
        yave = dobj.mean(ycol)
        ymed = dobj.median(ycol)
        yvar = dobj.var(ycol)
        ystd = dobj.std(ycol)
        ymid = (ymax + ymin)*0.5
        yppk = (ymax - ymin)
        z1 = dobj.unique_name("z")
        dobj.append(z1)
        z2 = dobj.unique_name("z")
        dobj.append(z2)
        z3 = dobj.unique_name("z")
        dobj.append(z3)
        dobj.set_parsed("%s = abs %s"  % (z1, ycol))
        dobj.set_parsed("%s = %s + %s" % (z2, ycol, z1))
        dobj.set_parsed("%s = %s - %s" % (z3, ycol, z1))
        dobj.set_parsed("%s = 0.5 * %s" % (z2, z2))
        dobj.set_parsed("%s = 0.5 * %s" % (z3, z3))
        yaba = dobj.time_average(xcol, z1)
        ypoa = dobj.time_average(xcol, z2)
        ynea = dobj.time_average(xcol, z3)
        #----------------------------------------------------------------------
        # timestep stats
        #----------------------------------------------------------------------
        npts  = dobj.nrows()
        dobj.set_parsed("%s = del %s" % (z1, xcol))
        dobj.set_entry(-1, z1, dobj.get_entry(-2, z1))
        dxmin = dobj.min(z1)
        dxmax = dobj.max(z1)
        #----------------------------------------------------------------------
        # signal delta stats
        #----------------------------------------------------------------------
        dobj.set_parsed("%s = del %s" % (z1, ycol))
        dobj.set_entry(0, z1, dobj.get_entry(1, z1))
        dymin = dobj.min(z1)
        dymax = dobj.max(z1)
        dobj.delete(z1, z2, z3)
        report = decida.interpolate("""
            Signal=$ycol time=$xcol:
              RMS                     $yrms
              Time-average            $yavg
              Time-abs-average        $yaba
              Time-pos-average        $ypoa
              Time-neg-average        $ynea
              Minimum                 $ymin
              Maximum                 $ymax
              Median                  $ymed
              Middle                  $ymid
              Peak-to-Peak            $yppk
              Average                 $yave
              Variance                $yvar
              Standard deviation      $ystd

              Number of data points   $npts
              Minimum time-step       $dxmin
              Maximum time-step       $dxmax
              Minimum |signal-delta|  $dymin
              Maximum |signal-delta|  $dymax
        """)
        report = re.sub("\n            ", "\n", report)
        print report
        ### tkMessageBox.showinfo(parent=self, message=report, title="statistics")
        MessageDialog(parent=self, message=report, title="statistics")
    #==========================================================================
    # METHOD  : __duty
    # PURPOSE : analysis -> Frequecy/Duty-cycle
    #==========================================================================
    def __duty(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # find level (default par)
        #----------------------------------------------------------------------
        ymin = dobj.min(ycol)
        ymax = dobj.max(ycol)
        level = 0.5*(ymax + ymin)
        #----------------------------------------------------------------------
        # freq/duty-cycle dialog
        #----------------------------------------------------------------------
        guititle = "Freq/Duty-Cycle Parameters"
        guispecs = [
            ["entry", "frequency/duty-cycle parameters",  [
                 ["level", "%s slice level" % ycol,  level],
            ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V = sd.go()
        if not V["ACCEPT"] :
            return
        level = float(V["level"])
        #----------------------------------------------------------------------
        # call duty cycle
        #----------------------------------------------------------------------
        dduty = dobj.periods(xcol, ycol, level)
        DataViewx(data=dduty)
    #==========================================================================
    # METHOD  : __edges
    # PURPOSE : analysis -> edges
    #==========================================================================
    def __edges(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # defaults
        #----------------------------------------------------------------------
        vhigh = dobj.max(ycol)
        vlow  = dobj.min(ycol)
        #----------------------------------------------------------------------
        # edges dialog
        #----------------------------------------------------------------------
        guititle = "Edges Parameters"
        guispecs = [
            ["entry", "edges parameters",  [
                 ["vhigh", "high %s value" % (ycol), vhigh],
                 ["vlow",  "low  %s value" % (ycol), vlow],
            ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V = sd.go()
        if not V["ACCEPT"] :
            return
        vlow  = float(V["vlow"])
        vhigh = float(V["vhigh"])
        #----------------------------------------------------------------------
        # call edges
        #----------------------------------------------------------------------
        dd = dobj.edges(xcol, ycol, vlow=vlow, vhigh=vhigh)
        if not dd is None :
            DataViewx(data=dd)
    #==========================================================================
    # METHOD  : __fft
    # PURPOSE : analysis -> FFT
    #==========================================================================
    def __fft(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        zcol = dobj.unique_name("%s_fft" % (ycol))
        #----------------------------------------------------------------------
        # FFT dialog
        #----------------------------------------------------------------------
        guititle = "FFT parameters"
        guispecs = [
            ["radio", "window function", "window", "hamming", [
                 ["bartlett window", "bartlett"],
                 ["blackman window", "blackman"],
                 ["hamming window",  "hamming"],
                 ["hanning window",  "hanning"],
            ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V = sd.go()
        if not V["ACCEPT"] :
            return
        window = V["window"]
        #----------------------------------------------------------------------
        # call fft
        #----------------------------------------------------------------------
        dfft = dobj.fft(zcol, ycol, xcol, window=window)
        DataViewx(data=dfft, command=[["frequency DB(%s)" % (zcol), "xaxis=\"log\""]])
    #==========================================================================
    # METHOD  : __period_time_average
    # PURPOSE : analysis -> Periodic Time-Average
    #==========================================================================
    def __period_time_average(self) :
        dobj = self.__data_obj
        time_col = self.__xcol_Var.get()
        sig_col  = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # period time average dialog
        #----------------------------------------------------------------------
        guititle = "Periodic time-average  parameters"
        guispecs = [
            ["entry", "input columns", [
                 ["time", "Time Column", time_col],
                 ["sig",  "Signal Column", sig_col],
            ]],
            ["entry", "Trigger column parameters (leave blank to use Period and Offset)", [
                 ["trig",  "Trigger Column", ""],
                 ["level", "Trigger Level", ""],
            ]],
            ["radio", "Trigger edge", "edge", "rising", [
                 ["Rising edge",  "rising"],
                 ["Falling edge", "falling"],
                 ["Both edges",   "both"],
            ]],
            ["entry", "Period and Offset", [
                 ["period", "Period", ""],
                 ["offset", "Offset", ""],
            ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V = sd.go()
        if not V["ACCEPT"] :
            return
        time_col = V["time"]
        sig_col  = V["sig"]
        trig_col = V["trig"]
        level    = V["level"]
        edge     = V["edge"]
        period   = V["period"]
        offset   = V["offset"]
        if trig_col != "" :
            if not trig_col in dobj.names() :
                self.warning("specified trigger column isn't in data array: cannot proceed")
                return
            trmax = dobj.max(trig_col)
            trmin = dobj.min(trig_col)
            if level == "" :
                level = (trmax + trmin)*0.5
                self.message("using trigger level = %s" % (level))
            else :
                level=float(level)
                if not (level > trmin) and not (level < trmax) :
                    self.warning("specified trigger level isn't within \"%s\" range: cannot proceed" % (trig_col))
                    return
            d1 = dobj.period_time_average(time_col, sig_col, 
                trigger=trig_col, level=level, edge=edge)
        else :
            if period == "" or offset == "" :
                self.warning("period and offset must be specified: cannot proceed")
                return
            period=float(period)
            offset=float(offset)
            if period <= 0.0 :
                self.warning("specified period is less than or equal to zero: cannot proceed")
                return
            d1 = dobj.period_time_average(time_col, sig_col, 
                period=period, offset=offset)
        if d1 is not None :
            DataViewx(data=d1)
    #==========================================================================
    # METHOD  : __inl_dnl
    # PURPOSE : analysis -> INL/DNL
    #==========================================================================
    def __inl_dnl(self) :
        dobj = self.__data_obj
        dig_col = self.__xcol_Var.get()
        ana_col = self.__ycol_Var.get()
        ref_col = dobj.unique_name("%s_ref" % (ana_col))
        inl_col = dobj.unique_name("%s_inl" % (ana_col))
        dnl_col = dobj.unique_name("%s_dnl" % (ana_col))
        #----------------------------------------------------------------------
        # INL_DNL dialog
        #----------------------------------------------------------------------
        guititle = "D to A parameters"
        guispecs = [
            ["entry", "input columns", [
                 ["dig", "Digital Column", dig_col],
                 ["ana", "Analog Column", ana_col],
            ]],
            ["entry", "output columns", [
                 ["ref", "Reference Column", ref_col],
                 ["inl", "INL Column", inl_col],
                 ["dnl", "DNL Column", dnl_col],
            ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V = sd.go()
        if not V["ACCEPT"] :
            return
        dig_col = V["dig"]
        ana_col = V["ana"]
        ref_col = V["ref"]
        inl_col = V["inl"]
        dnl_col = V["dnl"]
        #----------------------------------------------------------------------
        # calculations
        #----------------------------------------------------------------------
        dig_min = dobj.get_entry(0,  dig_col)
        dig_max = dobj.get_entry(-1, dig_col)
        ana_min = dobj.get_entry(0,  ana_col)
        ana_max = dobj.get_entry(-1, ana_col)
        dlsb = (ana_max-ana_min)/(dig_max-dig_min)
        print "LSB value = ", dlsb
        dobj.set("$ref_col = $ana_min + $dlsb*$dig_col")
        dobj.set("$inl_col = ($ana_col - $ref_col)/$dlsb")
        dobj.set("$dnl_col = del($ana_col)/$dlsb - 1")
        self.__add_data_col(ref_col)
        self.__add_data_col(inl_col)
        self.__add_data_col(dnl_col)
        self.__xcol_Var.set(dig_col)
        self.__ycol_Var.set(inl_col)
        self.__add_next()
        self.__ycol_Var.set(dnl_col)
        self.__add_overlay()
    #==========================================================================
    # METHOD  : __jitter
    # PURPOSE : analysis -> jitter
    #==========================================================================
    def __jitter(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # jitter dialog
        #----------------------------------------------------------------------
        guititle = "jitter parameters"
        guispecs = [
            ["entry", "input columns", [
                 ["time", "Time Column",   xcol],
                 ["sig",  "Signal Column", ycol],
            ]],
            ["radio", "signal type", "clk", "1", [
                 ["Clock Signal", "1"],
                 ["Data Signal",  "0"],
            ]],
            ["entry", "clock frequency/data_rate", [
                 ["freq", "Clock frequency/data-rate", 1e9],
            ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V = sd.go()
        if not V["ACCEPT"] :
            return
        time = V["time"]
        sig  = V["sig"]
        clk  = bool(int(V["clk"]))
        freq = float(V["freq"])
        #----------------------------------------------------------------------
        # calculations
        #----------------------------------------------------------------------
        V=dobj.jitter(time, sig, clock=clk, freq=freq, prt=False)
        report = V["report"]
        print report
        ### tkMessageBox.showinfo(parent=self, message=report, title="jitter")
        MessageDialog(parent=self, message=report, title="jitter")
    #==========================================================================
    # METHOD  : __time_constant
    # PURPOSE : analysis -> time-constant
    #==========================================================================
    def __time_constant(self) :
        pass
    #==========================================================================
    # METHOD  : __step_response
    # PURPOSE : analysis -> step-response
    #==========================================================================
    def __step_response(self) :
        pass
    #==========================================================================
    # METHOD  : __eye_diagram
    # PURPOSE : analysis -> eye-diagram
    #==========================================================================
    def __eye_diagram(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # find offset and period (default pars)
        #----------------------------------------------------------------------
        print "finding offset and period"
        xmin = dobj.min(xcol)
        xmax = dobj.max(xcol)
        ymin = dobj.min(ycol)
        ymax = dobj.max(ycol)
        level = 0.5*(ymax + ymin)
        yx = dobj.crossings(xcol, ycol, level)
        ny = len(yx)
        if ny >= 5 :
            offset = yx[0]
            ya = yx[ny-3]
            yb = yx[ny-1]
            period = yb - ya
        else :
            offset = 0
            period = xmax
        #----------------------------------------------------------------------
        # eye-diagram dialog
        #----------------------------------------------------------------------
        guititle = "Eye-diagram Parameters"
        guispecs = [
            ["entry", "eye-diagram parameters",  [
                 ["offset", "%s offset" % xcol,  offset],
                 ["period", "%s period" % ycol,  period],
            ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V = sd.go()
        if not V["ACCEPT"] :
            return
        offset = float(V["offset"])
        period = float(V["period"])
        #----------------------------------------------------------------------
        # generate eye diagram column
        #----------------------------------------------------------------------
        eye_col = "%s_eye" % (xcol)
        eye_col = dobj.unique_name(eye_col)
        dobj.eye_time(xcol, eye_col, period=period, offset=offset)
        self.__add_data_col(eye_col)
        self.__xcol_Var.set(eye_col)
        self.__add_next()
    #==========================================================================
    # METHOD  : __scope_diagram
    # PURPOSE : analysis -> oscilloscope-diagram
    #==========================================================================
    def __scope_diagram(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # find period (default pars)
        #----------------------------------------------------------------------
        print "finding period"
        xmin = dobj.min(xcol)
        xmax = dobj.max(xcol)
        ymin = dobj.min(ycol)
        ymax = dobj.max(ycol)
        level = 0.5*(ymax + ymin)
        yx = dobj.crossings(xcol, ycol, level)
        ny = len(yx)
        if ny >= 5 :
            ya = yx[ny-3]
            yb = yx[ny-1]
            period = yb - ya
        else :
            period = xmax
        #----------------------------------------------------------------------
        # scope-diagram dialog
        #----------------------------------------------------------------------
        guispecs = [
            ["entry", "oscilloscope-diagram parameters",  [
                 ["level",   "%s level"  % ycol, level],
                 ["period",  "%s period" % ycol, period],
            ]],
            ["radio", "Trigger edge", "edge", "rising", [
                 ["Rising edge",  "rising"],
                 ["Falling edge", "falling"],
                 ["Both edges",   "both"],
            ]],
        ]
        sd = SelectionDialog(self, title="Oscilloscope-diagram Parameters",
            guispecs=guispecs)
        V = sd.go()
        if not V["ACCEPT"] :
            return
        level  = string.atof(V["level"])
        period = string.atof(V["period"])
        edge   = V["edge"]
        #----------------------------------------------------------------------
        # generate scope diagram column
        #----------------------------------------------------------------------
        osc_col = "%s_osc" % (xcol)
        osc_col = dobj.unique_name(osc_col)
        dobj.osc_time(xcol, osc_col, ycol, period=period,
            level=level, edge=edge)
        self.__add_data_col(osc_col)
        self.__xcol_Var.set(osc_col)
        self.__add_next()
    #==========================================================================
    # METHOD  : __filter
    # PURPOSE : analysis -> filter
    #==========================================================================
    def __filter(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # default parameters
        #----------------------------------------------------------------------
        xdiff   = numpy.diff(dobj.get(xcol))
        xdelmin = numpy.min(xdiff)
        if xdelmin <= 0.0 :
            self.warning("data column \"%s\" is not strictly ascending: cannot proceed" % (xcol))
            return
        zcol = dobj.unique_name("filter_%s" % (ycol))
        fpole_max = 0.5/xdelmin
        fpole = 0.01 * fpole_max
        #----------------------------------------------------------------------
        # filter dialog
        #----------------------------------------------------------------------
        guititle = "Filter Parameters"
        guispecs = [
            ["entry", "filter parameters",  [
                 ["zcol",  "output filter column", zcol],
                 ["fpole", "pole frequency (maximum = %8.4g)" % fpole_max, fpole],
            ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V = sd.go()
        if not V["ACCEPT"] :
            return
        zcol  = V["zcol"]
        fpole = float(V["fpole"])
        #----------------------------------------------------------------------
        # call lpf
        #----------------------------------------------------------------------
        try:
            dobj.lpf(zcol, ycol, xcol, fpole)
        except RuntimeError:
            return
        self.__add_data_col(zcol)
        self.__ycol_Var.set(zcol)
        self.__add_next()
    #==========================================================================
    # METHOD  : __mavg_filter
    # PURPOSE : analysis -> mavg_filter
    #==========================================================================
    def __mavg_filter(self) :
        dobj = self.__data_obj
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # default parameters
        #----------------------------------------------------------------------
        zcol = dobj.unique_name("mavg_filter_%s" % (ycol))
        navg = 21
        #----------------------------------------------------------------------
        # filter dialog
        #----------------------------------------------------------------------
        guititle = "Moving-Average Filter Parameters"
        guispecs = [
            ["entry", "moving-average filter parameters",  [
                 ["zcol", "output filter column", zcol],
                 ["navg", "number of points in average", navg],
            ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V = sd.go()
        if not V["ACCEPT"] :
            return
        zcol  = V["zcol"]
        navg  = int(V["navg"])
        #----------------------------------------------------------------------
        # call moving_average_filter
        #----------------------------------------------------------------------
        try:
            dobj.moving_average_filter(zcol, ycol, navg=navg)
        except RuntimeError:
            return
        self.__add_data_col(zcol)
        self.__ycol_Var.set(zcol)
        self.__add_next()
    #==========================================================================
    # METHOD  : __linreg
    # PURPOSE : analysis -> linear regression
    #==========================================================================
    def __linreg(self) :
        book = self.__Component["book"]
        tabid = book.current_tab()
        xy   = self.__Plot[tabid]
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # default values
        #----------------------------------------------------------------------
        xmin, xmax, ymin, yax = xy.limits()
        zcol  = dobj.unique_name("linreg_%s_%s" % (ycol, xcol))
        #----------------------------------------------------------------------
        # selection dialog
        #----------------------------------------------------------------------
        guititle = "Linear Regression"
        guispecs = [
          ["entry", "output column", [
                 ["zcol", "Output Column", zcol],
                 ["xmin", "Minimum %s value" % (xcol), xmin],
                 ["xmax", "Maximum %s value" % (xcol), xmax],
          ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V=sd.go()
        if not V["ACCEPT"]:
            return
        zcol = V["zcol"]
        xmin = V["xmin"]
        xmax = V["xmax"]
        #----------------------------------------------------------------------
        # get regression coefficients
        #----------------------------------------------------------------------
        d1 = dobj.dup()
        d1.filter("(%s >= %g) && (%s <= %g)" % (xcol, xmin, xcol, xmax))
        V = d1.linreg(xcol, ycol)
        b0, b1 = V["coefficients"]
        report = V["report"]
        #----------------------------------------------------------------------
        # generate function
        #----------------------------------------------------------------------
        dobj.set("%s = %g + %g*%s" % (zcol, b0, b1, xcol))
        self.__add_data_col(zcol)
        self.__ycol_Var.set(zcol)
        self.__add_overlay(autoscale_x=False, autoscale_y=False)
        #----------------------------------------------------------------------
        # display report
        #----------------------------------------------------------------------
        print report
        MessageDialog(parent=self, message=report, title="linear regression")
    #==========================================================================
    # METHOD  : __quadreg
    # PURPOSE : analysis -> quadradic regression
    #==========================================================================
    def __quadreg(self) :
        book = self.__Component["book"]
        tabid = book.current_tab()
        xy   = self.__Plot[tabid]
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # default values
        #----------------------------------------------------------------------
        xmin, xmax, ymin, yax = xy.limits()
        zcol  = dobj.unique_name("quadreg_%s_%s" % (ycol, xcol))
        #----------------------------------------------------------------------
        # selection dialog
        #----------------------------------------------------------------------
        guititle = "Quadradic Regression"
        guispecs = [
          ["entry", "output column", [
                 ["zcol", "Output Column", zcol],
                 ["xmin", "Minimum %s value" % (xcol), xmin],
                 ["xmax", "Maximum %s value" % (xcol), xmax],
          ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V=sd.go()
        if not V["ACCEPT"]:
            return
        zcol = V["zcol"]
        xmin = V["xmin"]
        xmax = V["xmax"]
        #----------------------------------------------------------------------
        # get regression coefficients
        #----------------------------------------------------------------------
        d1 = dobj.dup()
        d1.filter("(%s >= %g) && (%s <= %g)" % (xcol, xmin, xcol, xmax))
        V = d1.quadreg(xcol, ycol)
        b0, b1, b2 = V["coefficients"]
        report = V["report"]
        #----------------------------------------------------------------------
        # generate function
        #----------------------------------------------------------------------
        dobj.set("%s = %g + %g*%s + %g*%s*%s" % \
            (zcol, b0, b1, xcol, b2, xcol, xcol))
        self.__add_data_col(zcol)
        self.__ycol_Var.set(zcol)
        self.__add_overlay(autoscale_x=False, autoscale_y=False)
        #----------------------------------------------------------------------
        # display report
        #----------------------------------------------------------------------
        print report
        MessageDialog(parent=self, message=report, title="quadradic regression")
    #==========================================================================
    # METHOD  : __four
    # PURPOSE : analysis -> fourier coefficients
    #==========================================================================
    def __four(self) :
        book = self.__Component["book"]
        tabid = book.current_tab()
        xy   = self.__Plot[tabid]
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # default values
        #----------------------------------------------------------------------
        xmin, xmax, ymin, yax = xy.limits()
        zcol  = dobj.unique_name("four_%s_%s" % (ycol, xcol))
        nfour = 8
        #----------------------------------------------------------------------
        # selection dialog
        #----------------------------------------------------------------------
        guititle = "Fourier Coefficients"
        guispecs = [
          ["entry", "output column", [
                 ["zcol",  "Output Column", zcol],
                 ["nfour", "Order of Fourier Expansion", nfour],
                 ["xmin", "Minimum %s value" % (xcol), xmin],
                 ["xmax", "Maximum %s value" % (xcol), xmax],
          ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V=sd.go()
        if not V["ACCEPT"]:
            return
        zcol  = V["zcol"]
        nfour = V["nfour"]
        xmin = V["xmin"]
        xmax = V["xmax"]
        #----------------------------------------------------------------------
        # get fourier coefficients
        #----------------------------------------------------------------------
        d1 = dobj.dup()
        d1.filter("(%s >= %g) && (%s <= %g)" % (xcol, xmin, xcol, xmax))
        V = d1.fourcoeff(xcol, ycol, nfour)
        coefficients = V["coefficients"]
        report = V["report"]
        #----------------------------------------------------------------------
        # generate function
        #----------------------------------------------------------------------
        T    = xmax - xmin
        pi   = math.acos(-1)
        wcol = zcol + "_PHI"
        f0 = coefficients.pop(0)
        dobj.set("%s = %g" % (zcol, f0))
        dobj.set("%s = %g" % (wcol, f0))
        for n in range(1, nfour+1) :
            fc = coefficients.pop(0)
            fs = coefficients.pop(0)
            dobj.set("%s = %s + %g*cos(%d*2*%g*%s/%g)" % (zcol, zcol, fc, n, pi, xcol, T))
            dobj.set("%s = %s + %g*sin(%d*2*%g*%s/%g)" % (zcol, zcol, fs, n, pi, xcol, T))
            fa = math.sqrt(fc*fc + fs*fs)
            fp = math.atan2(fc, fs)
            dobj.set("%s = %s + %g*sin(%d*2*%g*%s/%g + %g)" % (wcol, wcol, fa, n, pi, xcol, T, fp))
        self.__add_data_col(zcol)
        self.__ycol_Var.set(zcol)
        self.__add_overlay(autoscale_x=False, autoscale_y=False)
        self.__add_data_col(wcol)
        self.__ycol_Var.set(wcol)
        self.__add_overlay(autoscale_x=False, autoscale_y=False)
        #----------------------------------------------------------------------
        # display report
        #----------------------------------------------------------------------
        print report
        MessageDialog(parent=self, message=report, title="Fourier Expansion")
    #==========================================================================
    # METHOD  : __histogram
    # PURPOSE : analysis -> histogram
    #==========================================================================
    def __histogram(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # histogram dialog
        #----------------------------------------------------------------------
        guititle = "histogram parameters"
        guispecs = [
            ["entry", "Histogram", [
                   ["column",      "Sample column",  ycol],
                   ["nbins",       "Number of bins", 51],
                ]
            ],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V = sd.go()
        if not V["ACCEPT"] :
            return
        column = V["column"]
        nbins  = int(V["nbins"])
        #----------------------------------------------------------------------
        # call histogram
        #----------------------------------------------------------------------
        book        = self.__Component["book"]
        tab_text    = "%s_histogram" % (column)
        plotframe   = book.new_page(tab_text, lift=True)
        plot_width  = self["plot_width"]
        plot_height = self["plot_height"]
        hist = Histogramx(plotframe, command=[dobj, column], nbins=nbins,
            plot_width=plot_width, plot_height=plot_height)
        tabid=book.current_tab()
        self.__Plot[tabid] = hist
    #==========================================================================
    # METHOD  : __WAV
    # PURPOSE : analysis -> WAV
    #==========================================================================
    def __WAV(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        npts = dobj.nrows()
        #----------------------------------------------------------------------
        # default values
        #----------------------------------------------------------------------
        xmin = dobj.get_entry( 0, xcol)
        xmax = dobj.get_entry(-1, xcol)
        max_dvolume = float(pow(2, 15)-1)
        max_rvolume = 1.0
        output_file = ycol + ".wav"
        output_file = re.sub("[()]", "_", output_file)
        #----------------------------------------------------------------------
        # WAV dialog
        #----------------------------------------------------------------------
        guititle = "WAV parameters"
        guispecs = [
            ["entry", "WAV", [
                ["time_col",     "Time column",           xcol],
                ["signal_col",   "Signal column",         ycol],
                ["max_rvolume",  "Maximum volume [0:1]",  max_rvolume],
                ["output_file",  "Output .wav file",      output_file],
            ]],
            ["radio", "Sample rate", "sample_rate",      "44100", [
                ["44100", "44100"],
                ["96000", "96000"],
            ]],
            ["check", "warped time", [
                ["warp",         "Warp time",             True],
            ]],
            ["entry", "warped time", [
                ["nperiods",     "Number of periods in window", 1],
                ["base_freq",    "Base frequency [Hz]",   440],
                ["clip_length",  "Length of sound clip",  5.0],
            ]],
            ["entry", "non-warped time", [
                ["repetitions",  "Number of repetitions", 1],
            ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V = sd.go()
        if not V["ACCEPT"] :
            return
        time_col    = V["time_col"]
        signal_col  = V["signal_col"]
        nperiods    = int(V["nperiods"])
        base_freq   = float(V["base_freq"])
        max_rvolume = min(max(float(V["max_rvolume"]), 0.0), 1.0)
        sample_rate = int(V["sample_rate"])
        clip_length = float(V["clip_length"])
        output_file = re.sub("[()]", "_", V["output_file"])
        repetitions = int(V["repetitions"])
        warp        = V["warp"]

        if warp :
           duration = float(nperiods)/base_freq
           repetitions = int(clip_length/duration + 0.5) + 1
        else :
           duration = xmax-xmin
        #----------------------------------------------------------------------
        # generate wav
        # map tmin, tmax onto uniform time axis 0, duration
        # struct.pack: 'h' - data is formatted as short ints
        # setparams: n_channels, sample_width, frame_rate, n_frames,
        #     compression_type, compression_name
        # example:
        #   duration = 2.0
        #   nsamples = int(duration*sample_rate)
        #   nvector = numpy.arange(nsamples, dtype=numpy.float)
        #   signal_samples = (max_rvolume*max_dvolume)*\
        #       numpy.sin(2.0*numpy.pi*nvector*440.0/float(sample_rate))
        #----------------------------------------------------------------------
        nsamples = int(duration*sample_rate)
        if nsamples < 1 :
            self.warning("signal duration is too short to sample at %g %s\n" % (
                sample_rate, "samples/sec"))
            return
        #---------------------------------------------------------------------
        # map onto uniform time grid
        #---------------------------------------------------------------------
        xdata = decida.range_sample(xmin, xmax, num=nsamples)
        ydata = []
        n = 0
        for x in xdata :
            found = False
            while n < npts - 1 :
                xp = dobj.get_entry(n, xcol)
                if xp >= x:
                    found = True
                    break
                n += 1
            yp = dobj.get_entry(n, ycol)
            if found and n > 0 :
                xm = dobj.get_entry(n-1, xcol)
                ym = dobj.get_entry(n-1, ycol)
                yp = ym + (yp-ym)*(x-xm)/(xp-xm)
            ydata.append(yp)
        ymax=max(ydata) 
        ymin=min(ydata) 
        ymid=(ymax+ymin)/2.0
        yamp=(ymax-ymin)/2.0
        samp = int((max_rvolume/yamp)*max_dvolume)
        signal_samples = [samp*(y-ymid) for y in ydata] * repetitions
        #---------------------------------------------------------------------
        # push out to wave
        #---------------------------------------------------------------------
        import struct, wave
        nsamples = len(signal_samples)
        signal_buffer = struct.pack('h' * nsamples, *tuple(signal_samples))
        f = wave.open(output_file, "wb")
        f.setparams((1, 2, sample_rate, nsamples, "NONE", "noncompressed"))
        f.writeframes(signal_buffer)
        f.close()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # DataViewx GUI operations menu callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD  : __colops
    # PURPOSE : column operations
    #==========================================================================
    def __colops(self) :
        dobj = self.__data_obj
        #----------------------------------------------------------------------
        # selection dialog
        #----------------------------------------------------------------------
        sd_title = "Equation"
        sd_specs = [
          ["entry", "equation, (ex. z = x + y)", [
                 ["equation", "Equation", ""],
          ]],
          ["check", "parsed (only unary and binary operations)", [
                 ["parsed", "already parsed", False],
          ]],
        ]
        sd = SelectionDialog(self, title=sd_title, guispecs=sd_specs)
        V=sd.go()
        #----------------------------------------------------------------------
        # data object equation
        #----------------------------------------------------------------------
        if V["ACCEPT"] :
            parsed   = V["parsed"]
            equation = V["equation"]
            m=re.search("^([^=]+)=(.+)$", equation)
            if not m :
                self.warning("equation not in right format: LHS = RHS")
                return
            zcol = m.group(1)
            zcol = string.strip(zcol)
            if parsed :
                dobj.set_parsed(equation)
            else :
                dobj.set(equation)
            self.__add_data_col(zcol)
            self.__ycol_Var.set(zcol)
            self.__add_next()
    #--------------------------------------------------------------------------
    # METHOD  : __a2d
    # PURPOSE : analog to digital
    #--------------------------------------------------------------------------
    def __a2d(self) :
        dobj = self.__data_obj
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # default parameters
        #----------------------------------------------------------------------
        col_spec = ycol
        slice    = 0.5*(dobj.min(ycol) + dobj.max(ycol))
        invert   = False
        zcol     = dobj.unique_name("a2d")
        #----------------------------------------------------------------------
        # HSpice, SSpice
        #----------------------------------------------------------------------
        m = re.search("^v\(([^<]+)<([^>]+)>\)", col_spec)
        if m :
            zcol = m.group(1)
            bits = []
            for col in dobj.names() :
                mx = re.search("^v\(%s<([^>]+)>\)" % (zcol), col)
                if mx:
                    bits.append(int(mx.group(1)))
            col_spec = "v(%s<%s:%s>)" % (zcol, max(bits), min(bits))
        #----------------------------------------------------------------------
        # spectre
        #----------------------------------------------------------------------
        m = re.search("^([^<]+)<([^>]+)>", col_spec)
        if m :
            zcol = m.group(1)
            bits = []
            for col in dobj.names() :
                mx = re.search("^%s<([^>]+)>" % (zcol), col)
                if mx:
                    bits.append(int(mx.group(1)))
            col_spec = "%s<%s:%s>" % (zcol, max(bits), min(bits))
        #----------------------------------------------------------------------
        # selection dialog
        #----------------------------------------------------------------------
        sd_title = "Analog to Digital parameters"
        sd_specs = [
          ["entry", "A to D: V(node<msb:lsb>) or list of columns", [
                 ["col_spec", "Analog column(s)",       col_spec],
                 ["slice",    "Analog slice value",     slice   ],
                 ["zcol",     "Output digital column",  zcol    ],
          ]],
          ["check", "", [
                 ["invert", "dig value low for analog value > slice",  invert],
          ]],
        ]
        sd = SelectionDialog(self, title=sd_title, guispecs=sd_specs)
        V=sd.go()
        #----------------------------------------------------------------------
        # data object a2d
        #----------------------------------------------------------------------
        if V["ACCEPT"] :
            col_spec = V["col_spec"]
            slice    = string.atof(V["slice"])
            zcol     = V["zcol"]
            invert   = V["invert"]
            dobj.a2d(zcol, col_spec, slice)
            self.__add_data_col(zcol)
            self.__ycol_Var.set(zcol)
            self.__add_next()
    #--------------------------------------------------------------------------
    # METHOD  : __delineator
    # PURPOSE : new column toggles value when other columns change
    #--------------------------------------------------------------------------
    def __delineator(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # default parameters
        #----------------------------------------------------------------------
        col = ycol
        vlo, vhi = -1000, 1000
        #----------------------------------------------------------------------
        # selection dialog
        #----------------------------------------------------------------------
        sd_title = "Add delineator column"
        sd_specs = [
          ["entry", "", [
                 ["col", "column to delineate",   col],
                 ["vlo", "low delineator value",  vlo],
                 ["vhi", "high delineator value", vhi],
          ]],
        ]
        sd = SelectionDialog(self, title=sd_title, guispecs=sd_specs)
        V=sd.go()
        #----------------------------------------------------------------------
        # create delineator column
        #----------------------------------------------------------------------
        if V["ACCEPT"] :
            col      = V["col"]
            vlo      = float(V["vlo"])
            vhi      = float(V["vhi"])
            zcol     = dobj.unique_name("%s_delineator" % (col))
            tcol     = dobj.unique_name("tmp")
            dobj.set("%s = del(%s) != 0.0" % (tcol, col))
            dobj.set("%s = 0.0" % (zcol))
            z = 0
            for i in range(0, dobj.nrows()) :
                if dobj.get_entry(i, tcol) != 0.0 :
                    z = 1 - z
                dobj.set_entry(i, zcol, vlo+(vhi-vlo)*z)
            dobj.delete(tcol)
            self.__add_data_col(zcol)
            self.__ycol_Var.set(zcol)
            self.__add_overlay(autoscale_x=False, autoscale_y=False)
    #--------------------------------------------------------------------------
    # METHOD  : __neg_x
    # PURPOSE : negate x column
    #--------------------------------------------------------------------------
    def __neg_x(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        dobj.set_parsed("%s = - %s" % (xcol, xcol))
        self.__add_overlay()
    #--------------------------------------------------------------------------
    # METHOD  : __neg_y
    # PURPOSE : negate y column
    #--------------------------------------------------------------------------
    def __neg_y(self) :
        dobj = self.__data_obj
        ycol = self.__ycol_Var.get()
        dobj.set_parsed("%s = - %s" % (ycol, ycol))
        self.__add_overlay()
    #--------------------------------------------------------------------------
    # METHOD  : __abs_x
    #--------------------------------------------------------------------------
    # PURPOSE : absolute value x column
    def __abs_x(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        dobj.set_parsed("%s = abs %s" % (xcol, xcol))
        self.__add_overlay()
    #--------------------------------------------------------------------------
    # METHOD  : __neg_y
    # PURPOSE : absolute value y column
    #--------------------------------------------------------------------------
    def __abs_y(self) :
        dobj = self.__data_obj
        ycol = self.__ycol_Var.get()
        dobj.set_parsed("%s = abs %s" % (ycol, ycol))
        self.__add_overlay()
    #--------------------------------------------------------------------------
    # METHOD  : __inv_y
    # PURPOSE : z = 1/y
    #--------------------------------------------------------------------------
    def __inv_y(self) :
        dobj = self.__data_obj
        ycol = self.__ycol_Var.get()
        zcol = dobj.unique_name("invert_" + ycol)
        dobj.set_parsed("%s = 1 / %s" % (zcol, ycol))
        self.__add_data_col(zcol)
        self.__ycol_Var.set(zcol)
        self.__add_next()
    #--------------------------------------------------------------------------
    # METHOD  : __delta_x
    # PURPOSE : z = del x
    #--------------------------------------------------------------------------
    def __delta_x(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        zcol = dobj.unique_name("delta_" + xcol)
        dobj.set_parsed("%s = del %s" % (zcol, xcol))
        self.__add_data_col(zcol)
        self.__ycol_Var.set(zcol)
        self.__add_next()
    #--------------------------------------------------------------------------
    # METHOD  : __deriv_y_x
    # PURPOSE : z = y dY/dX x 
    #--------------------------------------------------------------------------
    def __deriv_y_x(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        zcol = dobj.unique_name("deriv_%s_%s" % (ycol, xcol))
        dobj.set_parsed("%s = %s dY/dX %s" % (zcol, ycol, xcol))
        self.__add_data_col(zcol)
        self.__ycol_Var.set(zcol)
        self.__add_next()
    #--------------------------------------------------------------------------
    # METHOD  : __integ_y_x
    # PURPOSE : z = y integ x
    #--------------------------------------------------------------------------
    def __integ_y_x(self) :
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        zcol = dobj.unique_name("integ_%s_%s" % (ycol, xcol))
        dobj.set_parsed("%s = %s integ %s" % (zcol, ycol, xcol))
        self.__add_data_col(zcol)
        self.__ycol_Var.set(zcol)
        self.__add_next()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # DataViewx GUI plot button callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #--------------------------------------------------------------------------
    # METHOD  : __del
    # PURPOSE : delete the current tab/plot
    #--------------------------------------------------------------------------
    def __del(self) :
        book = self.__Component["book"]
        tabid = book.current_tab()
        xy = self.__Plot[tabid]
        del xy
        del  self.__Plot[tabid]
        book.del_page()
    #--------------------------------------------------------------------------
    # METHOD  : __delete_points
    # PURPOSE : end_stretch callback to delete data points
    #--------------------------------------------------------------------------
    def __delete_points(self, u1, v1, u2, v2) :
        book = self.__Component["book"]
        tabid = book.current_tab()
        xy   = self.__Plot[tabid]
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        #----------------------------------------------------------------------
        # check to see if x and y column are on the plot!
        #----------------------------------------------------------------------
        curves = xy.curves()
        xcolcs = []
        ycolcs = []
        for curve in curves :
            A = xy.curve_attributes(curve)
            xcolcs.append(A["xname"])
            ycolcs.append(A["yname"])
        if not xcol in xcolcs :
            self.warning("x-column \"%s\" isn't on the current plot" % (xcol))
            return
        if not ycol in ycolcs :
            self.warning("y-column \"%s\" isn't on the current plot" % (ycol))
            return
        #----------------------------------------------------------------------
        # filter data
        #----------------------------------------------------------------------
        x1, y1 = xy.plot_uv_xy(u1, v1)
        x2, y2 = xy.plot_uv_xy(u2, v2)
        xmin = min(x1, x2)
        xmax = max(x1, x2)
        ymin = min(y1, y2)
        ymax = max(y1, y2)
        dobj.filter(
            "(%s < (%e)) || (%s > (%e)) || (%s < (%e)) || (%s > (%e))" % \
            (xcol, xmin, xcol, xmax, ycol, ymin, ycol, ymax))
        #----------------------------------------------------------------------
        # replot all curves
        #----------------------------------------------------------------------
        cc = xy.current_curve()
        for curve in curves :
            A = xy.curve_attributes(curve)
            xy.delete_curve(curve, redraw=False)
            xy.add_curve(dobj, A["xname"], A["yname"],
                autoscale_x=False, autoscale_y=False,
                lstate=A["lstate"], sstate=A["sstate"],
                color=A["color"], symbol=A["symbol"], ssize=A["ssize"],
                wline=A["wline"], trace=A["trace"])
        xy.current_curve(cc)
        self.__data_modified()
    #--------------------------------------------------------------------------
    # METHOD  : __stack_all
    # PURPOSE : stack all curves
    # NOTES : THIS IS NOT IMPLEMENTED YET
    #--------------------------------------------------------------------------
    def __stack_all(self) :
        book = self.__Component["book"]
        tabid = book.current_tab()
        xy   = self.__Plot[tabid]
        dobj = self.__data_obj
        curves = xy.curves()
        cc = xy.current_curve()
        for curve in curves :
            A = xy.curve_attributes(curve)
            xy.delete_curve(curve, redraw=False)
            xy.add_curve(dobj, A["xname"], A["yname"],
                autoscale_x=False, autoscale_y=True,
                lstate=A["lstate"], sstate=A["sstate"],
                color=A["color"], symbol=A["symbol"], ssize=A["ssize"],
                wline=A["wline"], trace=A["trace"])
        xy.current_curve(cc)
    #--------------------------------------------------------------------------
    # METHOD  : __overlay_all
    # PURPOSE : overlay all curves
    # NOTES : THIS IS NOT IMPLEMENTED YET
    #--------------------------------------------------------------------------
    def __overlay_all(self) :
        book = self.__Component["book"]
        tabid = book.current_tab()
        xy   = self.__Plot[tabid]
        dobj = self.__data_obj
        curves = xy.curves()
        cc = xy.current_curve()
        for curve in curves :
            A = xy.curve_attributes(curve)
            xy.delete_curve(curve, redraw=False)
            xy.add_curve(dobj, A["xname"], A["yname"],
                autoscale_x=False, autoscale_y=True,
                lstate=A["lstate"], sstate=A["sstate"],
                color=A["color"], symbol=A["symbol"], ssize=A["ssize"],
                wline=A["wline"], trace=A["trace"])
        xy.current_curve(cc)
    #--------------------------------------------------------------------------
    # METHOD  : __add_next
    # PURPOSE : add a new tab/plot
    #--------------------------------------------------------------------------
    def __add_next(self, args=None) :
        book = self.__Component["book"]
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        tab_text    = "%s_%s"    % (ycol, xcol)
        plotframe   = book.new_page(tab_text, lift=True)
        plot_width  = self["plot_width"]
        plot_height = self["plot_height"]
        colspec     = "%s %s" % (xcol, ycol)
        if args is None :
            xy = XYplotx(plotframe, command = [dobj, colspec],
                plot_width=plot_width, plot_height=plot_height)
        else :
            xy = eval(
                "XYplotx(plotframe, command = [dobj, colspec], %s, \
                plot_width=plot_width, plot_height=plot_height)" % (args)
            )
        #-----------------------------------------------------------------
        # book.current_tab() : need to wait until page is displayed
        #-----------------------------------------------------------------
        tabid       = book.current_tab()
        self.__Plot[tabid] = xy
        #-----------------------------------------------------------------
        # add one more stretch binding to the XYplotx canvas:
        # ctrl-mouse 3: delete points
        #-----------------------------------------------------------------
        def cmd1(event, xy=xy):
            xy.begin_stretch("delete", self.__delete_points, event.x, event.y)
        def cmd2(event, xy=xy):
            xy.continue_stretch(event.x, event.y)
        def cmd3(event, self=self):
            xy.end_stretch(event.x, event.y)
        xycanv = xy.plot_window()
        xycanv.bind("<Control-ButtonPress-3>",   cmd1)
        xycanv.bind("<B3-Motion>",               cmd2)
        xycanv.bind("<Control-ButtonRelease-3>", cmd3)
    #--------------------------------------------------------------------------
    # METHOD  : __add_start
    # PURPOSE : start again with current plot
    #--------------------------------------------------------------------------
    def __add_start(self) :
        book  = self.__Component["book"]
        tabid = book.current_tab()
        if not tabid :
            self.__add_next()
            return
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        xy   = self.__Plot[tabid]
        curves = xy.curves()
        for curve in curves :
            xy.delete_curve(curve, redraw=False)
        xy.add_curve(dobj, xcol, ycol, start=True,
            autoscale_x=True, autoscale_y=True, strict=True)
        tab_text    = "%s_%s"    % (ycol, xcol)
        book.relabel_current_tab(tab_text)
    #--------------------------------------------------------------------------
    # METHOD  : __add_overlay
    # PURPOSE : add curve to current plot
    #--------------------------------------------------------------------------
    def __add_overlay(self, autoscale_x=False, autoscale_y=True) :
        book  = self.__Component["book"]
        tabid = book.current_tab()
        if not tabid :
            self.__add_next()
            return
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        xy   = self.__Plot[tabid]
        curves = xy.curves()
        curve_name = "data_%d_:_%s_vs_%s" % (1, ycol, xcol)
        if curve_name in curves :
            A = xy.curve_attributes(curve_name)
            xy.delete_curve(curve_name, redraw=False)
            xy.add_curve(dobj, xcol, ycol,
                autoscale_x=autoscale_x, autoscale_y=autoscale_y, strict=False,
                lstate=A["lstate"], sstate=A["sstate"],
                color=A["color"], symbol=A["symbol"], ssize=A["ssize"],
                wline=A["wline"], trace=A["trace"])
        else :
            xy.add_curve(dobj, xcol, ycol,
                autoscale_x=autoscale_x, autoscale_y=autoscale_y, strict=False)
    #--------------------------------------------------------------------------
    # METHOD  : __add_stack
    # PURPOSE : stack plots
    #--------------------------------------------------------------------------
    def __add_stack(self, autoscale_x=False, autoscale_y=True) :
        book  = self.__Component["book"]
        tabid = book.current_tab()
        if not tabid :
            self.__add_next()
            return
        dobj = self.__data_obj
        xcol = self.__xcol_Var.get()
        ycol = self.__ycol_Var.get()
        xy     = self.__Plot[tabid]
        curves = xy.curves()
        #--------------------------------------------------------------------
        # this shouldn't happen unless all curves are deleted in current plot
        #--------------------------------------------------------------------
        if len(curves) == 0 :
            self.__add_start()
            return
        curve_name = "data_%d_:_%s_vs_%s" % (1, ycol, xcol)
        if curve_name in curves :
            #--------------------------------------------------
            # don't have to stack if only curve is existing one
            #--------------------------------------------------
            if len(curves) == 1 : return
            A = xy.curve_attributes(curve_name)
            xy.delete_curve(curve_name, redraw=False)
            keep_attr = True
        else :
            keep_attr = False
        #----------------------------------------------------------------------
        # find current limits (should be xy.curve_limits() when that is avail.)
        # find increment to separate curves
        #----------------------------------------------------------------------
        xmin, xmax, ymin, ymax = xy.limits()
        ylow = dobj.min(ycol)
        yinc = 0.0
        m     = re.search("^data_(.+)_:_(.+)_vs_(.+)$", curves[0])
        if m:
           ycol0 = m.group(2)
           yinc  = (dobj.max(ycol0) - dobj.min(ycol0))*0.10
        if yinc == 0.0 : yinc = (ymax - ymin)*0.10
        if yinc == 0.0 : yinc = 0.10
        #----------------------------------------------------------------------
        # create new stacked curve
        #----------------------------------------------------------------------
        d1 = dobj.dup()
        d1.select(xcol, ycol)
        d1.set_parsed("%s = %s + %g"  % (ycol, ycol, (ymax + yinc - ylow)))
        if keep_attr :
            xy.add_curve(d1, xcol, ycol,
                autoscale_x=autoscale_x, autoscale_y=autoscale_y, strict=False,
                lstate=A["lstate"], sstate=A["sstate"],
                color=A["color"], symbol=A["symbol"], ssize=A["ssize"],
                wline=A["wline"], trace=A["trace"])
        else :
            xy.add_curve(d1, xcol, ycol,
                autoscale_x=autoscale_x, autoscale_y=autoscale_y, strict=False)
    #--------------------------------------------------------------------------
    # METHOD  : __add_data_col
    # PURPOSE : data column was added, revise table
    #--------------------------------------------------------------------------
    def __add_data_col(self, zcol) :
        if not zcol in self.__table_names :
            self.__data_modified()
            self.__table_names.append(zcol)
            table  = self.__Component["table"]
            xtable = self.__Component["xtable"]
            ytable = self.__Component["ytable"]
            rb = Radiobutton(xtable, text=zcol, anchor=W, width=30,
                variable= self.__xcol_Var, value=zcol)
            rb.pack(side=TOP)
            rb.pack(side=TOP, fill=X)
            rb.bind("<MouseWheel>", self.__mouse_wheel)
            rb.bind("<Button-4>",   self.__mouse_wheel)
            rb.bind("<Button-5>",   self.__mouse_wheel)
            rb.bind("<Prior>",      self.__page_key)
            rb.bind("<Next>",       self.__page_key)
            rb.bind("<Home>",       self.__page_key)
            rb.bind("<End>",        self.__page_key)
            rb = Radiobutton(ytable, text=zcol, anchor=W, width=30,
                variable= self.__ycol_Var, value=zcol)
            rb.pack(side=TOP)
            rb.pack(side=TOP, fill=X)
            rb.bind("<MouseWheel>", self.__mouse_wheel)
            rb.bind("<Button-4>",   self.__mouse_wheel)
            rb.bind("<Button-5>",   self.__mouse_wheel)
            rb.bind("<Prior>",      self.__page_key)
            rb.bind("<Next>",       self.__page_key)
            rb.bind("<Home>",       self.__page_key)
            rb.bind("<End>",        self.__page_key)
            self.after_idle(self.__adjust_table)
    #--------------------------------------------------------------------------
    # METHOD  : __del_data_col
    # PURPOSE : data column was deleted, revise table
    #--------------------------------------------------------------------------
    def __del_data_col(self, zcol) :
        if zcol in self.__table_names :
            iz = self.__table_names.index(zcol)
            self.__table_names.pop(iz)
            table  = self.__Component["table"]
            #------------------------------------------------------------------
            # destroy radio buttons
            #------------------------------------------------------------------
            xtable = self.__Component["xtable"]
            ytable = self.__Component["ytable"]
            xrbs=xtable.winfo_children()
            yrbs=ytable.winfo_children()
            for xrb in xrbs :
                if xrb["text"] == zcol :
                    xrb.destroy()
            for yrb in yrbs :
                if yrb["text"] == zcol :
                    yrb.destroy()
            #------------------------------------------------------------------
            # revise selected x and y columns
            #------------------------------------------------------------------
            xcol = self.__xcol_Var.get()
            ycol = self.__ycol_Var.get()
            if xcol == zcol :
                ix = max(0, iz-1)
                xcol = self.__table_names[ix]
                self.__xcol_Var.set(xcol)
            if ycol == zcol :
                iy = max(0, iz-1)
                ycol = self.__table_names[iy]
                self.__ycol_Var.set(ycol)
            self.after_idle(self.__adjust_table)
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # DataViewx GUI help button callback method
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #--------------------------------------------------------------------------
    # METHOD  : __help_cmd
    # PURPOSE : help callback
    #--------------------------------------------------------------------------
    def __help_cmd(self) :
        #--------------------------------------------------------------------
        # locate help directory
        #--------------------------------------------------------------------
        ok = False
        for d in sys.path :
            dir = "%s/decida/dataview_help/" % (d)
            if os.path.isdir(dir) :
                ok = True
                break
        if not ok :
            self.warning("can't locate help information")
            return
        #--------------------------------------------------------------------
        # get list of files to display (TableOfContents is in hyperhelp format)
        #--------------------------------------------------------------------
        fok = False
        files = []
        Label = {}
        f = open("%s/%s" % (dir, "TableOfContents"))
        for line in f :
            if   re.match("^ *%% *hyperhelp_link_frame +{", line):
               fok = True
            elif re.match("^ *} *%%", line):
               fok = False
            elif fok :
               line = re.sub("[{}\"]", "", line)
               line = string.strip(line)
               line = string.split(line)
               file=line[-1]
               files.append(file)
               Label[file] = string.join(line[:-1])
        f.close()
        #--------------------------------------------------------------------
        # display files
        #--------------------------------------------------------------------
        hfn = FrameNotebook(tab_location="right", wait_to_display=True, destroy=False)
        for file in files:
            label = Label[file]
            dfile = "%s/%s" % (dir, file)
            TextWindow(hfn.new_page(label), file=dfile)
        hfn.lift_tab(Label[files[0]])
        hfn.wait("dismiss")
        hfn.__del__()
        del hfn
