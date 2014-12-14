################################################################################
# CLASS    : Calc
# PURPOSE  : calculator
# AUTHOR   : Richard Booth
# DATE     : Sat Nov  9 11:17:45 2013
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
import string
import random
from math    import *
from decida.ItclObjectx import ItclObjectx
import Tkinter
from Tkinter import *    
import tkMessageBox

class Calc(ItclObjectx, Frame) :
    """ calculator.

    **synopsis**:

    Calc is an algebraic-mode calculator with 50 buttons, a small
    menu of additional functions, a menu of constants, and a help display.
    Calc instances can be embedded in other Tkinter windows.  The calculators
    can be operated with mouse or keyboard entry.

    The DeCiDa application *calc* simply instantiates one Calc object.

    **constructor arguments**:

        .. option:: parent (Tkinter handle) (default=None)

              handle of frame or other widget to pack plot in.
              if this is not specified, top-level is created.

        .. option:: \*\*kwargs (dict)

              keyword=value specifications:
              options or configuration-options

    **options**:

        .. option::  wait (bool, default=True)

              If True, wait in main-loop until window is destroyed.
        
    **configuration options**:

        .. option::  verbose (bool, default=False)

              Enable/disable verbose mode.  (Not currently used.)

    **example**:

        >>> from decida.Calc import Calc
        >>> Calc()

    **buttons**:

        .. option:: OFF

            Dismiss the calculator.  Shuts down the main-loop.     

        .. option:: AC

            All clear: clear display accumulator, memory accumulator,
            and calculator stack.

        .. option:: CE

            Clear entry: clear display accumulator.

        .. option:: HELP

            Display help window: button / keystroke map.

        .. option:: MENU

            Menu of additional functions.  Currently these are:

            * random number:

                Enter a random number between 0 and 1 into the
                display accumulator.

            * random seed:

                Use the display accumulator value as a random seed.

            * list stack:

                Display the calculator stack.

            * set precision:

                Use the display accumulator value as a number of digits
                of precision in calculator evaluations.

            * logging:

                Open a file to log the calculator evaluations.

        .. option:: const

            Display constant dialog.  Double click on a constant to enter it
            into the display accumulator.

        .. option:: put

            Put the current display accumulator number into constant memory.
            The const button can then be used to access its value.

        .. option:: pi

            Enter pi into the display accumulator.
            
        .. option:: e

            Enter e into the display accumulator.

        .. option:: DRG

            Change from degrees to radians to grads for trigonometric functions.

        .. option:: HYP

            Toggle hyperbolic mode.
            If sin, cos, or tan buttons are then
            invoked, the evaluation is of sinh, cosh, or tanh.
            If arc and hyperbolic mode are both on, then
            evaluation is of asinh, acosh, or atanh.

        .. option:: ARC

            Toggle arc mode.
            If sin, cos, or tan buttons are then
            invoked, the evaluation is of asin, acos, or atan.
            If arc and hyperbolic mode are both on, then
            evaluation is of asinh, acosh, or atanh.

        .. option:: sin cos tan

            Trigonometric, inverse-trigonometric (arc mode on),
            hyperbolic (hyperbolic mode on), or inverse-hyperbolic
            (arc and hyperbolic modes both on).

        .. option:: sqrt

            Square root of the display accumulator.

        .. option:: x!

            Factorial of the (integer value of the) display accumulator.
            
        .. option:: 10^x

            10 to the power of the display accumulator.

        .. option:: exp

            e to the power of the display accumulator.

        .. option:: x^2

            Square of the display accumulator.

        .. option:: 1/x

            Inverse of the display accumulator.

        .. option:: log

            Logarithm to the base ten of the display accumulator.

        .. option:: ln

            Natural logarithm of the display accumulator.

        .. option:: y^x

            Push the current display accumulator value onto the stack,
            evaluate the stack value raised to the power of the display
            accumulator value.

        .. option:: M+

            Add the display accumulator to the memory accumulator.

        .. option:: M-

            Subtract the display accumulator from the memory accumulator.

        .. option:: STO

            Store the display accumulator to the memory accumulator.
    
        .. option:: RCL

            Recall the memory accumulator to the display accumulator.

        .. option:: XCH

            Exchange the memory accumulator with the display accumulator.

        .. option:: CLR

            Clear the memory accumulator.

        .. option:: ( )

            Algebraic parentheses.

        .. option:: 0 1 2 3 4 5 6 7 8 9 EE +/-

            Numerical entry.

        .. option:: + - * /

            Binary arithmetic operations.

        .. option:: =

            Evaluate the calculator stack.

    **public methods**:

        * public methods from *ItclObjectx*

    """
    nrows = 10
    ncols = 5
    buttons = string.split("""
        OFF  HELP const pi   AC    
        DRG  MENU put   e    CE    
        HYP  sin  cos   tan  sqrt  
        ARC  x!   10^x  exp  x^2   
        M+   1/x  log   ln   y^x   
        M-   EE   (     )    /     
        STO  7    8     9    *     
        RCL  4    5     6    -     
        XCH  1    2     3    +     
        CLR  0    .     +/-  =     
    """)
    buttoncommands = string.split("""
        OFF  HELP const pi   AC   
        DRG  MENU put   e    CE   
        HYP  trig trig  trig sqrt 
        ARC  fact tenx  exp  sqr  
        Mp   inv  log   ln   ytox 
        Mm   EE   lpar  rpar mdiv 
        STO  num  num   num  mdiv 
        RCL  num  num   num  pmin 
        XCH  num  num   num  pmin 
        CLR  num  pt    porm eq   
    """)
    buttonbindings = string.split("""
        Control-Key-q       H           less        numbersign  A           
        d                   question    greater     at          C           
        h                   s           c           t           r           
        a                   exclam      X           x           dollar      
        Control-Key-p       percent     L           l           asciicircum 
        Control-Key-m       e           parenleft   parenright  slash       
        Control-Key-s       Key-7       Key-8       Key-9       asterisk    
        Control-Key-r       Key-4       Key-5       Key-6       minus       
        Control-Key-x       Key-1       Key-2       Key-3       plus        
        Control-Key-c       Key-0       period      asciitilde  equal       
    """)
    menuentries = [
        ["random number",  "RAND"],
        ["random seed",    "SEED"],
        ["list stack",     "STKQ"],
        ["set precision",  "PREC"],
        ["logging",        "LOG" ],
    ]
    constants = [
        "273.16           Tabs          T(O deg C) deg K",
        "1.380622e-23     kB   (J/K)    boltzmann constant",
        "8.61708e-05      kB   (eV/K)   boltzmann constant",
        "6.58218e-16      hbar (eV-s)   planck constant",
        "2.99792e+10      co   (cm/s)   speed of light in vacuum",
        "1.602192e-19     qe   (C)      unit charge",
        "8.854215e-14     eo   (F/cm)   permittivity of free space",
        "9.10956e-31      mo   (kg)     electron rest mass",
        "11.7             ksi           relative permittivity (Si)",
        "3.9              kox           relative permittivity (SiO2)",
        "1.03594315e-12   esi  (F/cm)   permittivity (Si)",
        "3.45314385e-13   eox  (F/cm)   permittivity (SiO2)",
    ]
    _bm_pi   = None
    _bm_sqrt = None
    @staticmethod
    def __create_bitmaps() :
        if not Tkinter._default_root :
            root = Tk()
            root.wm_state("withdrawn")
        Calc._bm_pi = Image("bitmap")
        Calc._bm_pi["data"] = """
            #define bm_pi_width 16
            #define bm_pi_height 16
            static char bm_pi_bits[] = {
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0xfe, 0x3f, 0x12, 0x04, 0x10, 0x04, 0x10, 0x04,
                0x10, 0x04, 0x10, 0x04, 0x10, 0x04, 0x10, 0x04,
                0x10, 0x04, 0x10, 0x04, 0x1c, 0x04, 0x00, 0x00
            };
        """
        Calc._bm_sqrt = Image("bitmap")
        Calc._bm_sqrt["data"] = """
            #define bm_sqrt_width 16
            #define bm_sqrt_height 16
            static char bm_sqrt_bits[] = {
                0x00, 0x00, 0x00, 0x00, 0x00, 0x7e, 0x00, 0x02,
                0x00, 0x02, 0x00, 0x03, 0x00, 0x01, 0x00, 0x01,
                0x87, 0x01, 0x8c, 0x00, 0x98, 0x00, 0xf0, 0x00,
                0x60, 0x00, 0x40, 0x00, 0x40, 0x00, 0x00, 0x00
            };
        """
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Calc main
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
        self.__parent    = parent
        self.__Component = {}
        self.__log       = False
        self.__saved_constants = []
        self.__wait      = True
        #----------------------------------------------------------------------
        # configuration options:
        #----------------------------------------------------------------------
        self._add_options({
            "verbose" : [False, None],
        })
        #----------------------------------------------------------------------
        # keyword arguments are *not* all configuration options
        #----------------------------------------------------------------------
        for key, value in kwargs.items() :
            if key == "wait" :
                self.__wait = value
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
    # Calc configuration option callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Calc GUI
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def __gui(self) :
        #---------------------------------------------------------------------
        # top-level:
        #---------------------------------------------------------------------
        if not self.__parent :
            if not Tkinter._default_root :
                root = Tk()
                root.wm_state("withdrawn")
            self.__toplevel = Toplevel()
            Frame.__init__(self, self.__toplevel, class_ = "Calc")
        else:
            self.__toplevel = None
            Frame.__init__(self, self.__parent,   class_ = "Calc")
        self.pack(side=TOP, fill=BOTH, expand=True)
        #---------------------------------------------------------------------
        # bitmaps
        #---------------------------------------------------------------------
        if Calc._bm_pi is None :
            Calc.__create_bitmaps()
        #---------------------------------------------------------------------
        # option database:
        #---------------------------------------------------------------------
        #---------------------------------------------------------------------
        # main layout
        #---------------------------------------------------------------------
        display = Frame(self)
        states  = Frame(self)
        buttons = Frame(self)
        display.pack(side=TOP, fill=X, expand=True)
        states.pack(side=TOP, fill=X, expand=True)
        buttons.pack(side=TOP, fill=BOTH, expand=True)
        #---------------------------------------------------------------------
        # calculator display
        #---------------------------------------------------------------------
        disp = Entry(display,
            bd=2, relief=SUNKEN, state=DISABLED,
            background="GhostWhite", foreground="black")
        disp.pack(side=TOP, padx=1, pady=1, expand=True, fill=BOTH)
        disp["disabledforeground"] = "black"
        self.__Component["disp"] = disp
        #---------------------------------------------------------------------
        # calculator states
        #---------------------------------------------------------------------
        for state in ["a", "h", "d", "m", "s"] :
            lst = Label(states, background="steel blue", foreground="white")
            lst.pack(side=LEFT, fill=X, expand=True)
            self.__Component["state_" + state] = lst
        #---------------------------------------------------------------------
        # calculator buttons
        #---------------------------------------------------------------------
        def focuscmd(event) :
            event.widget.focus_set()
        def unfocuscmd(event) :
            Tkinter._default_root.focus_set()
        def eqcmd(event, self=self) :
            self.eq("=")
        def bscmd(event, self=self) :
            self.BS()
        def selcmd(event, self=self) :
            x=self.selection_get()
            self.STX(x)
            self.eq("=")
        for i, button in enumerate(Calc.buttons) :
            x = i % Calc.ncols
            y = i / Calc.ncols
            if (button == "MENU") :
               b = Menubutton(buttons,
                   text=button,
                   relief=RAISED, bd=2, pady=2, padx=2, highlightthickness=0,
                   background="dark khaki", foreground="black")
               m = Menu(b,
                   background="red", foreground="white")
               b["menu"] = m
               for label, c in Calc.menuentries :
                   def cmd(self=self, command = c) :
                       cx = compile("self.%s()" % (command), "string", "single")
                       eval(cx)
                   m.add_command(label=label, command=cmd)
            else :
               c=Calc.buttoncommands[i]
               e=Calc.buttonbindings[i]
               def cmd(self=self, command=c, button=button) :
                   cx = compile(
                       "self.%s(\"%s\")" % (command, button), "string", "single"
                   )
                   eval(cx)
               b = Button(buttons,
                   command=cmd,
                   relief=RAISED, bd=2, pady=1, padx=1, highlightthickness=0,
                   background="dark khaki", foreground="black")
               if   button == "pi" :
                   b["image"] = Calc._bm_pi
               elif button == "sqrt" :
                   b["image"] = Calc._bm_sqrt
               else :
                   b["text"] = button
               if sys.platform == "darwin" :
                   b["width"] = 7
               else :
                   b["width"] = 5
               def cmde(event, self=self, command=c, button=button) :
                   cx = compile(
                       "self.%s(\"%s\")" % (command, button), "string", "single"
                   )
                   eval(cx)
               self.bind("<" + e + ">" , cmde)
            b.bind("<Enter>", focuscmd)
            b.bind("<Leave>", unfocuscmd)
            bx = list(b.bindtags())
            bx.insert(0, self)
            b.bindtags(tuple(bx))
            b.grid(column=x, row=y, sticky=N+S+E+W)
        #---------------------------------------------------------------------
        # calculator bindings
        #---------------------------------------------------------------------
        for c in ["disp", "state_a", "state_h", "state_d", "state_m", "state_s"] :
            w = self.__Component[c]
            w.bind("<Enter>", focuscmd)
            w.bind("<Leave>", unfocuscmd)
            wx = list(w.bindtags())
            wx.insert(0, self)
            w.bindtags(tuple(wx))
        self.bind("<Return>",          eqcmd)
        self.bind("<space>",           eqcmd)
        self.bind("<BackSpace>",       bscmd)
        self.bind("<Delete>",          bscmd)
        self.bind("<Double-Button-2>", selcmd)
        self.AC("AC")
        #---------------------------------------------------------------------
        # update / mainloop
        #---------------------------------------------------------------------
        if self.__toplevel:
            self.__toplevel.wm_title("calc")
        if self.__wait :
            self.wait_window()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Calc buttons callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #===========================================================================
    # METHOD  : num
    # PURPOSE : enter one digit of a number
    #===========================================================================
    def num (self, button) :
        if (self.mode == ">") :
            self.x = []
            self.x.append(button)
            self.mode = "I"
        elif (self.mode in ["I", "F"]) :
            self.x.append(button)
        elif (self.mode in ["E", "X"]) :
            e=self.x.pop()
            self.x.pop()
            self.x.append(e)
            self.x.append(button)
            self.mode = "X"
        self.__dispx__()
    #===========================================================================
    # METHOD  : pt
    # PURPOSE : decimal point
    #===========================================================================
    def pt (self, button) :
        if (self.mode == ">") :
            self.x = []
            self.x.append("0")
            self.x.append(".")
            self.mode = "F"
        elif (self.mode == "I") :
            self.x.append(".")
            self.mode = "F"
        self.__dispx__()
    #===========================================================================
    # METHOD  : EE
    # PURPOSE : enter exponent
    #===========================================================================
    def EE (self, button) :
        if (self.mode in ["I", "F"]) :
            self.x.append("E")
            self.x.append("+")
            self.x.append("0")
            self.x.append("0")
            self.mode = "E"
        self.__dispx__()
    #===========================================================================
    # METHOD  : porm
    # PURPOSE : enter +/-
    #===========================================================================
    def porm (self, button) :
        if (self.mode in [">", "I", "F"]) :
            if (self.x[0] == "-") :
               self.x.pop(0)
            else :
               self.x.insert(0, "-")
        elif (self.mode in ["E", "X"]) :
            if (self.x[-3] == "+") :
                self.x[-3] = "-"
            elif (self.x[-3] == "-") :
                self.x[-3] = "+"
        self.__dispx__()
    #===========================================================================
    # METHOD  : OFF
    # PURPOSE : shut down
    #===========================================================================
    def OFF (self, button) :
        self.quit()
        if self.__toplevel :
            self.__toplevel.destroy()
        else :
            self.destroy()
    #===========================================================================
    # METHOD  : CE
    # PURPOSE : clear entry
    #===========================================================================
    def CE (self, button) :
        self.CLX()
    #===========================================================================
    # METHOD  : AC
    # PURPOSE : clear all
    #===========================================================================
    def AC (self, button) :
        self.CLX()
        self.CLM()
        self.CLA()
        self.STK = []
    #===========================================================================
    # METHOD  : pi
    # PURPOSE : enter pi
    #===========================================================================
    def pi (self, button) :
        self.STX(pi)
    #===========================================================================
    # METHOD  : e
    # PURPOSE : enter e
    #===========================================================================
    def e (self, button) :
        self.STX(exp(1))
    #===========================================================================
    # METHOD  : const
    # PURPOSE : display constant dialog
    #===========================================================================
    def const (self, button) :
      u = self.constant()
      if not u is None :
         self.STX(u)
    #===========================================================================
    # METHOD  : put
    # PURPOSE : put accumulator into constant database
    #===========================================================================
    def put (self, button) :
      x = self.GTX()
      self.__saved_constants.append(
          "%-16s               saved result" % (str(x)))
    #===========================================================================
    # METHOD  : sqr
    # PURPOSE : x^2
    #===========================================================================
    def sqr (self, button) :
      x = self.GTX()
      self.STX(x*x)
    #===========================================================================
    # METHOD  : sqrt
    # PURPOSE : sqrt(x)
    #===========================================================================
    def sqrt (self, button) :
      x = self.GTX()
      if (x < 0) :
         self.messagebox("error: x<0")
      else :
         self.STX(sqrt(x))
    #===========================================================================
    # METHOD  : inv
    # PURPOSE : 1/x
    #===========================================================================
    def inv (self, button) :
      x = self.GTX()
      if (x == 0) :
         self.messagebox("error: x=0")
      else :
         self.STX(1.0/x)
    #===========================================================================
    # METHOD  : tenx
    # PURPOSE : 10^x
    #===========================================================================
    def tenx (self, button) :
      x = self.GTX()
      self.STX(10.0**x)
    #===========================================================================
    # METHOD  : exp
    # PURPOSE : e^x
    #===========================================================================
    def exp (self, button) :
      x = self.GTX()
      self.STX(exp(x))
    #===========================================================================
    # METHOD  : log
    # PURPOSE : log10(x)
    #===========================================================================
    def log (self, button) :
      x = self.GTX()
      if (x <= 0) :
        self.messagebox("error: x<=0")
      else :
        self.STX(log10(x))
    #===========================================================================
    # METHOD  : ln
    # PURPOSE : ln(x)
    #===========================================================================
    def ln (self, button) :
      x = self.GTX()
      if (x <= 0) :
        self.messagebox("error: x<=0")
      else :
        self.STX(log(x))
    #===========================================================================
    # METHOD  : ytox
    # PURPOSE : y^x
    #===========================================================================
    def ytox (self, button) :
      x = self.GTX()
      self.PSH(str(x))
      self.PSH("**")
      self.mode = ">"
      self.__dispx__()
    #===========================================================================
    # METHOD  : fact
    # PURPOSE : x!
    #===========================================================================
    def fact (self, button) :
      x = self.GTX()
      if ((x < 0) or (x > 170)) :
          self.messagebox("error: x<0 or x>170")
      else :
          u = 1.0
          for i in range(1, int(x+1)) :
              u *= i
          self.STX(u)
    #===========================================================================
    # METHOD  : trig
    # PURPOSE : sin/cos/tan, asin/acos/atan, sinh/cosh/tanh, asinh/acosh/atanh
    #===========================================================================
    def trig (self, button) :
      x = self.GTX()
      if (not(self.hyp)) :
          if   (self.drg == 0) :
              f = pi/180.0
          elif (self.drg == 1) :
              f = 1.0
          elif (self.drg == 2) :
              f = pi/200.0
          if (not(self.arc)) :
              x = eval(button + "(" + str(f) + "*" + str(x) + ")")
              self.STX(x)
          else :
              x = eval("a" + button + "(" + str(x) + ")" + "/" + str(f))
              self.STX(x)
      else :
          if (not(self.arc)) :
              x = eval(button + "h" + "(" + str(x) + ")")
              self.STX(x)
          else :
              x = eval(compile("self.a" + button + "h" + "(" + str(x) + ")",
                "string", "single"))
              self.STX(x)
      self.arc = 0
      self.hyp = 0
    #===========================================================================
    # METHOD  : pmin
    # PURPOSE : +,-
    #===========================================================================
    def pmin(self, button) :
      if (self.mode == "E") :
          self.x[-3] = button
          self.__dispx__()
      else :
          x = self.GTX()
          self.PSH(str(x))
          x = self.PEX(["("])
          self.STX(x)
          x = self.GTX()
          self.PSH(str(x))
          self.PSH(button)
    #===========================================================================
    # METHOD  : mdiv
    # PURPOSE : *,/
    #===========================================================================
    def mdiv(self, button) :
        x = self.GTX()
        self.PSH(str(x))
        x = self.PEX(["-", "+", "("])
        self.STX(x)
        x = self.GTX()
        self.PSH(str(x))
        self.PSH(button)
    #===========================================================================
    # METHOD  : lpar
    # PURPOSE : (
    #===========================================================================
    def lpar(self, button) :
       if (self.mode == ">") :
           self.PSH(button)
    #===========================================================================
    # METHOD  : rpar
    # PURPOSE : )
    #===========================================================================
    def rpar(self, button) :
       x = self.GTX()
       self.PSH(str(x))
       x = self.PEX(["("])
       self.STX(x)
       self.POP()
    #===========================================================================
    # METHOD  : eq
    # PURPOSE : =
    #===========================================================================
    def eq (self, button) :
        x = self.GTX()
        self.PSH(str(x))
        x = self.PEX()
        self.STX(x)
    #===========================================================================
    # METHOD  : HELP
    # PURPOSE : display help dialog
    #===========================================================================
    def HELP(self, button) :
        text = []
        text.append("Button:\tKey-binding:\n")
        text.append("----------------------------\n")
        for button, binding in zip(Calc.buttons, Calc.buttonbindings) :
            text.append(button + "\t" + binding + "\n")
        text.append("=\t<Return>\n")
        text.append("=\t<space>\n")
        self.messagebox(string.join(text, ""))
    #===========================================================================
    # METHOD  : DRG
    # PURPOSE : degree/radian/grad
    #===========================================================================
    def DRG(self, button) :
       self.drg = (self.drg + 1) % 3
       self.__dispa__()
    #===========================================================================
    # METHOD  : ARC
    # PURPOSE : arc
    #===========================================================================
    def ARC(self, button) :
       self.arc = not(self.arc)
       self.__dispa__()
    #===========================================================================
    # METHOD  : HYP
    # PURPOSE : hy
    #===========================================================================
    def HYP(self, button) :
       self.hyp = not(self.hyp)
       self.__dispa__()
    #===========================================================================
    # METHOD  : Mp
    # PURPOSE : add to memory
    #===========================================================================
    def Mp(self, button) :
       x = self.GTX()
       m = self.GTM()
       m = m + x
       self.STM(m)
    #===========================================================================
    # METHOD  : Mm
    # PURPOSE : subtract from memory
    #===========================================================================
    def Mm(self, button) :
       x = self.GTX()
       m = self.GTM()
       m = m - x
       self.STM(m)
    #===========================================================================
    # METHOD  : STO
    # PURPOSE : store in memory
    #===========================================================================
    def STO(self, button) :
       x = self.GTX()
       self.STM(x)
    #===========================================================================
    # METHOD  : RCL
    # PURPOSE : recall from memory
    #===========================================================================
    def RCL(self, button) :
       m = self.GTM()
       self.STX(m)
    #===========================================================================
    # METHOD  : XCH
    # PURPOSE : exchange accumulator and memory
    #===========================================================================
    def XCH(self, button) :
       x = self.GTX()
       m = self.GTM()
       self.STX(m)
       self.STM(x)
    #===========================================================================
    # METHOD  : CLR
    # PURPOSE : clear memory
    #===========================================================================
    def CLR(self, button) :
       self.CLM()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # binding and menu commands
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #===========================================================================
    # METHOD  : BS
    # PURPOSE : back-space
    #===========================================================================
    def BS(self) :
       x = string.join(self.x, "")
       if (len(x) == 1) :
           self.CLX()
           return()
       if   (self.mode == "I") :
           c = x[-2]
           if (c == "+" or c == "-") :
              self.CLX()
           else :
              u = x[:-1]
              self.x = [u]
       elif (self.mode == "F") :
           if x[-1] == "." :
              u = x[:-1]
              self.x = [u]
              self.mode = "I"
           else :
              u = x[:-1]
              self.x = [u]
       elif (self.mode == "X" or self.mode == "E") :
           u = x[:-4]
           self.x = [u]
           if (string.find(u, ".") >= 0) :
               self.mode = "F"
           else :
               self.mode = "I"
       self.__dispx__()
    #===========================================================================
    # METHOD  : RAND
    # PURPOSE : enter a random-number
    #===========================================================================
    def RAND(self) :
        self.STX(random.random())
    #===========================================================================
    # METHOD  : SEED
    # PURPOSE : use accumulator as a random seed
    #===========================================================================
    def SEED(self) :
        x=self.GTX()
        random.seed(x)
    #===========================================================================
    # METHOD  : STKQ
    # PURPOSE : print out stack
    #===========================================================================
    def STKQ(self) :
        text = []
        text.append("LOC:\tVALUE:\nX:\t" + str(self.x) + "\n")
        text.append("----------------------------\n")
        for i, entry in enumerate(self.STK) :
            text.append(str(i) + ":\t" + entry)
        self.messagebox(string.join(text, ""))
    #===========================================================================
    # METHOD  : PREC
    # PURPOSE : use accumulator to set precision
    #===========================================================================
    def PREC(self) :
        if ((self.x < 1) or (self.x >= 18)) :
            self.messagebox("error: x < 1 or x >= 18")
        else :
            p = int(self.x)
            tcl_precision = p
            self.messagebox("PRECISION = " + str(p))
    #===========================================================================
    # METHOD  : LOG
    # PURPOSE : toggle log file mode
    #===========================================================================
    def LOG(self) :
          self.logfile = "calc.py.log"
          if not self.__log :
              self.__log = True
              self.__logfid = open(self.logfile, "w")
              self.messagebox("log file \"" + self.logfile + "\" opened")
          else :
              self.__log = False
              self.__logfid.close()
              self.messagebox("log file \"" + self.logfile + "\" closed")
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # basic calculator functions
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD  : PSH
    # PURPOSE : push token onto stack
    #==========================================================================
    def PSH (self, token) :
       self.STK.append(token)
    #==========================================================================
    # METHOD  : POP
    # PURPOSE : pop token from stack
    #==========================================================================
    def POP (self) :
       return self.STK.pop()
    #==========================================================================
    # METHOD  : PEX
    # PURPOSE : pop expression from stack (stop before Stop)
    #==========================================================================
    def PEX (self, Stop=[""]) :
        e = []
        while (len(self.STK) > 0) :
           t = self.POP()
           if (t in Stop) :
               self.PSH(t)
               break
           if (t != "NOP") :
               e.insert(0, t)
        e = string.join(e, "")
        if (len(e) > 0) :
            x = eval(e)
            return x
        else :
            return 0.0
    #==========================================================================
    # METHOD  : STX
    # PURPOSE : set accumulator
    #==========================================================================
    def STX (self, x) :
        self.x = []
        self.x.append(str(x))
        self.mode = ">"
        self.__dispx__()
        if (self.__log) :
            u = string.join(self.x, "")
            self.__logfid.write("expression:" + u)
            self.__logfid.flush()
    #==========================================================================
    # METHOD  : STM
    # PURPOSE : set memory
    #==========================================================================
    def STM (self, m) :
        self.m = m
        self.mem = 1
        self.__dispm__()
        self.mode = ">"
        self.__dispx__()
    #=======================================================================
    # METHOD  : CLX
    # PURPOSE : clear accumulator
    #==========================================================================
    def CLX(self) :
        self.x = ["0"]
        self.mode = ">"
        self.__dispx__()
    #==========================================================================
    # METHOD  : CLM
    # PURPOSE : clear memory
    #==========================================================================
    def CLM (self) :
        self.m = 0
        self.mem = 0
        self.__dispm__()
    #=======================================================================
    # METHOD  : CLA
    # PURPOSE : clear states
    #==========================================================================
    def CLA(self) :
        self.drg = 0
        self.hyp = 0
        self.arc = 0
        self.__dispa__()
    #==========================================================================
    # METHOD  : GTX
    # PURPOSE : return accumulator
    # NOTES   :
    #     *  put decimal point on end of x if still in integer mode
    #        before further processing
    #==========================================================================
    def GTX (self) :
        if (self.mode == "I") :
            self.x.append(".")
            self.mode = "F"
            self.__dispx__()
        x = eval(string.join(self.x, ""))
        return x
    #==========================================================================
    # METHOD  : GTM
    # PURPOSE : return memory
    #==========================================================================
    def GTM (self) :
        if (not(self.mem)) :
            self.m = 0
            self.mem = True
            self.__dispm__()
        return self.m
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # extra math functions
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD  : asinh
    # PURPOSE : asinh
    #==========================================================================
    def asinh(self, x) :
        return log(x + sqrt(x*x + 1.0))
    #==========================================================================
    # METHOD  : acosh
    # PURPOSE : acosh
    #==========================================================================
    def acosh(self, x) :
        return log(x + sqrt(x*x - 1.0))
    #==========================================================================
    # METHOD  : atanh
    # PURPOSE : atanh
    #==========================================================================
    def atanh(self, x) :
        if (x == 1.0) :
            return 100.0
        else :
            return log(sqrt((1.0 + x)/(1.0 - x)))
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # windows
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD  : __dispx__
    # PURPOSE : re-display accumulator, mode
    #==========================================================================
    def __dispx__(self) :
        x = string.join(self.x, "")
        disp   = self.__Component["disp"]
        stat_s = self.__Component["state_s"]
        disp["state"] = NORMAL
        disp.delete(0, END)
        disp.insert(0, x)
        disp["state"] = DISABLED
        stat_s["text"] = self.mode
    #==========================================================================
    # METHOD  : __dispm__
    # PURPOSE : re-display memory
    #==========================================================================
    def __dispm__(self) :
        stat_m = self.__Component["state_m"]
        if (self.mem) :
            stat_m["text"] = "MEM"
        else :
            stat_m["text"] = ""
    #==========================================================================
    # METHOD  : __dispa__
    # PURPOSE : re-display drg, hyp, arc
    #==========================================================================
    def __dispa__(self) :
        stat_d = self.__Component["state_d"]
        stat_a = self.__Component["state_a"]
        stat_h = self.__Component["state_h"]
        if   (self.drg == 0) :
            stat_d["text"] = "DEG"
        elif (self.drg == 1) :
            stat_d["text"] = "RAD"
        else :
            stat_d["text"] = "GRD"
        if (self.arc) :
            stat_a["text"] = "ARC"
        else :
            stat_a["text"] = ""
        if (self.hyp) :
            stat_h["text"] = "HYP"
        else :
            stat_h["text"] = ""
    #==========================================================================
    # METHOD  : messagebox
    # PURPOSE : display error or info
    #==========================================================================
    def messagebox(self, message) :
        tkMessageBox.showinfo(message=message)
    #==========================================================================
    # METHOD  : constant
    # PURPOSE : constant toplevel
    #==========================================================================
    def constant(self) :
        #self.messagebox("constant isn't implemented yet")
        #---------------------------------------------------------------------
        # toplevel
        #---------------------------------------------------------------------
        top = Toplevel()
        top.protocol('WM_DELETE_WINDOW', self.__constant_cancel)
        self.__Component["constant_top"] = top
        #---------------------------------------------------------------------
        # basic frames
        #---------------------------------------------------------------------
        tf = Frame(top, bd=3, relief=GROOVE)
        tf.pack(side=TOP, fill=X, expand=True)
        mf = Frame(top, bd=3, relief=FLAT)
        mf.pack(side=TOP, fill=BOTH, expand=True)
        bf = Frame(top, bd=3, relief=FLAT, bg="cadet blue")
        bf.pack(side=TOP, fill=X, expand=True)
        #---------------------------------------------------------------------
        # title
        #---------------------------------------------------------------------
        tf_l = Label(tf, bitmap="question")
        tf_l.pack(side=LEFT, fill=BOTH, expand=True)
        tf_m = Label(tf, justify=LEFT)
        tf_m.pack(side=RIGHT, fill=BOTH, expand=True)
        tf_m["text"] = "select constant with <Double-Button-1>"
        #---------------------------------------------------------------------
        # listbox/scrollbar
        #---------------------------------------------------------------------
        yscr=Scrollbar(mf, orient=VERTICAL) 
        xscr=Scrollbar(mf, orient=HORIZONTAL)
        yscr.pack(side=RIGHT,  expand=True, fill=Y)
        xscr.pack(side=BOTTOM, expand=True, fill=X)
        lbox = Listbox(mf, relief=RAISED, height=15, width=60)
        lbox.pack(side=LEFT, expand=True, fill=BOTH)
        yscr.set(0, 0)
        xscr.set(0, 0)
        yscr["command"] = lbox.yview
        xscr["command"] = lbox.xview
        lbox["yscrollcommand"] = yscr.set
        lbox["xscrollcommand"] = xscr.set
        lbox["font"] = "Courier"
        self.__Component["constant_lbox"] = lbox
        #---------------------------------------------------------------------
        # accept and cancel buttons
        #---------------------------------------------------------------------
        bf_cancel = Frame(bf, bd=2, relief=SUNKEN)
        bf_cancel.pack(side=LEFT, expand=True, padx=3, pady=2)
        bf_cancel_button = Button(bf_cancel, text="cancel")
        bf_cancel_button.pack(anchor="c", expand=True, padx=3, pady=2)

        bf_accept = Frame(bf, bd=2, relief=SUNKEN)
        bf_accept.pack(side=LEFT, expand=True, padx=3, pady=2)
        bf_accept_button = Button(bf_accept, text="accept")
        bf_accept_button.pack(anchor="c", expand=True, padx=3, pady=2)

        bf_cancel_button["command"] =  self.__constant_cancel
        bf_accept_button["command"] =  self.__constant_accept
        #---------------------------------------------------------------------
        # bindings
        #---------------------------------------------------------------------
        def cmd(event, self=self) :
            self.__constant_accept()
        lbox.bind("<Double-Button-1>", cmd)
        self.__constant_results = None
        for constant in Calc.constants :
            lbox.insert(END, constant)
        for constant in self.__saved_constants :
            lbox.insert(END, constant)
        lbox.activate(0)
        lbox.selection_set(0)
        top.grab_set()
        top.mainloop()
        top.destroy()
        del self.__Component["constant_top"]
        del self.__Component["constant_lbox"]
        return self.__constant_results
    #==========================================================================
    # METHOD  : __constant_accept
    # PURPOSE : constant dialog accept button callback
    #==========================================================================
    def __constant_accept(self) :
        top  = self.__Component["constant_top"]
        lbox = self.__Component["constant_lbox"]
        results = lbox.get("active")
        results = string.split(results)[0]
        self.__constant_results = results
        top.quit()
    #==========================================================================
    # METHOD  : __constant_cancel
    # PURPOSE : constant dialog cancel button callback
    #==========================================================================
    def __constant_cancel(self) :
        top  = self.__Component["constant_top"]
        self.__constant_results = None
        top.quit()
