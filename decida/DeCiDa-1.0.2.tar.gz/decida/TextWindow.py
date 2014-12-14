################################################################################
# CLASS    : TextWindow
# PURPOSE  : text window for interactive session
# AUTHOR   : Richard Booth
# DATE     : Sat Nov  9 11:26:11 2013
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
##############################################################################
import user
import decida
import sys
import os
import os.path
import string
import re
import subprocess
from decida.ItclObjectx      import ItclObjectx
from decida.SelectionDialog  import SelectionDialog
from decida.FrameNotebook    import FrameNotebook
import Tkinter
from Tkinter import *
import tkFileDialog
import tkColorChooser
import tkSimpleDialog

class TextWindow(ItclObjectx, Frame) :
    """ text window graphical user-interface.

    **synopsis**:

    TextWindow is a graphical user-interface wrapper around the Tkinter
    *Text* widget.  On menus, it provides several ways to reformat the
    displayed text, such as lining up rows, (true) wrapping text, piping
    the text through sort, awk, or some other command.  TextWindow also has
    text searching and text highlighting.  And there are many other tools.

    The DeCiDa application *twin* simply instantiates one TextWindow object.

    **constructor arguments**:

        .. option:: parent (Tkinter object default=None)

            handle of frame or other widget to pack text-window in.
            If this is not specified, top-level is created.

        .. option:: \*\*kwargs (dict)

            configuration-options or option

    **options**:

        .. option:: file (string)

            name of file to read into text-window

    **results**:

        * Sets up text window with menu at top.

        * Configures binding for sending commands to program when user types
           return.

    **configuration options**:

        .. option:: verbose (bool, default=False)

            enable verbose mode

        .. option:: text_height (int, default=24)

            Height of TextWindow window in chars

        .. option:: text_width (int, default=80)

            Width of TextWindow window in chars

        .. option:: text_background (string, default="GhostWhite")

            Background of TextWindow window

        .. option:: text_foreground (string, default="blue")

            Foreground of TextWindow window

        .. option:: progcmd (string, default="")

            Prefix of command to send user-input to program.
            **The progcmd capability is not yet implemented.**

        .. option:: prompt (string, default=">")

            Prompt to place in text window.
            **The progcmd capability is not yet implemented.**

        .. option:: wait (bool, default=False)

            wait in main-loop until window is destroyed

        .. option:: destroy (bool, default=False)

            destroy main window

    **example**:

        >>> twin = TextWindow(wait=False)
        >>> twin.enter("abc")
        >>> twin.wait()
    
    **public methods**:

        * public methods from *ItclObjectx*

    """
    @staticmethod
    def linecol(linespec) :
        """ convert a linespec into line and column

        **arguments**:

            .. option:: linespec (string)

                Tk line-specification string in the format line.col

        **results**:

            * returns the line, col where line and col are integers

        """
        sline, scol = string.split(linespec, ".")
        line = string.atoi(sline)
        col  = string.atoi(scol)
        return line, col
    @staticmethod
    def is_commented(s, comment_char="#") :
        """ return true if line begins with a comment character.
        
        **arguments**:

            .. option:: s (string)

                A line of text

            .. option:: comment_char (string, default="#")

                The specified comment character

        **results**:

            *  If the specified comment character is the first character
               in s, return True, else False.

        """
        s = string.strip(s)
        return True if len(s) < 1 or s[0] == comment_char else False
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # TextWindow main
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
        self.__parent     = parent
        self.__Component  = {}
        self.__highlighted_lines   = {}
        self.__highlight_color     = "yellow"
        self.__comment_char        = "#"
        self.__truewrap_linelength = 80
        self.__savefile   = ""
        self.__wrapMode   = None
        #----------------------------------------------------------------------
        # configuration options:
        #----------------------------------------------------------------------
        if sys.platform == "darwin" :
            text_width  = 80
            text_height = 24
        else :
            text_width  = 80
            text_height = 24
        self._add_options({
            "verbose"        : [False, None],
            "text_width"     : [text_width,   self._config_text_width_callback],
            "text_height"    : [text_height,  self._config_text_height_callback],
            "text_background": ["GhostWhite", self._config_text_bg_callback],
            "text_foreground": ["black",      self._config_text_fg_callback],
            "progcmd"        : ["",           self._config_progcmd_callback],
            "prompt"         : [">",          None],
            "wait"           : [False,        None],
            "destroy"        : [True,         None],
        })
        #----------------------------------------------------------------------
        # keyword arguments are *not* all configuration options
        # file: command-line option to open file:
        #----------------------------------------------------------------------
        self.__openfile = None
        for key, value in kwargs.items() :
            if key == "file" :
                self.__openfile = value
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
    # TextWindow configuration option callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #===========================================================================
    # METHOD  : _config_text_height_callback
    # PURPOSE : configure text height
    #===========================================================================
    def _config_text_height_callback(self) :
        if not self.__Component :
            return
        height = self["text_height"]
        text = self.__Component["text"]
        text["height"] = height
    #===========================================================================
    # METHOD  : _config_text_width_callback
    # PURPOSE : configure text width
    #===========================================================================
    def _config_text_width_callback(self) :
        if not self.__Component :
            return
        width = self["text_width"]
        text = self.__Component["text"]
        text["width"]  = width
    #===========================================================================
    # METHOD  : _config_text_bg_callback
    # PURPOSE : configure text background
    #===========================================================================
    def _config_text_bg_callback(self) :
        if not self.__Component :
            return
        background = self["text_background"]
        text = self.__Component["text"]
        text["background"]  = background
    #===========================================================================
    # METHOD  : _config_text_fg_callback
    # PURPOSE : configure text foreground
    #===========================================================================
    def _config_text_fg_callback(self) :
        if not self.__Component :
            return
        foreground = self["text_foreground"]
        text = self.__Component["text"]
        text["foreground"]  = foreground
    #===========================================================================
    # METHOD  : _config_progcmd_callback
    # PURPOSE : configure progcmd
    #===========================================================================
    def _config_progcmd_callback(self) :
        if not self.__Component :
            return
        progcmd = self["progcmd"]
        if progcmd == "" :
            # bind TextProg <Return> ""
            pass
        else :
            # text = self.__Component["text"]
            # bind TextProg <Return> self.progcmd_return
            # bindtags text "Text TextProg text top all"
            # text.insert(endtext, self["prompt"])
            # text.mark_set(begtext, endtext)
            # text.mark_set(insert, endtext)
           pass
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # TextWindow GUI
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD  : __gui
    # PURPOSE : build graphical user interface
    #==========================================================================
    def __gui(self) :
        #---------------------------------------------------------------------
        # top-level:
        #---------------------------------------------------------------------
        if self.__parent == None :
            if not Tkinter._default_root :
                root = Tk()
                root.wm_state("withdrawn")
            self.__toplevel = Toplevel()
            Frame.__init__(self, self.__toplevel, class_ = "TextWindow")
            self.__toplevel.protocol('WM_DELETE_WINDOW', self.__quit_cmd)
            if not self.was_configured("wait") :
                self["wait"] = True
        else :
            self.__toplevel = None
            Frame.__init__(self, self.__parent,   class_ = "TextWindow")
            if not self.was_configured("wait") :
                self["wait"] = False
        self.pack(side=TOP, fill=BOTH, expand=True)
        #---------------------------------------------------------------------
        # option database:
        #---------------------------------------------------------------------
        if sys.platform == "darwin" :
            self.option_add("*TextWindow*Text.font", "Courier 20 bold")
            self.option_add("*TextWindow*Entry.font", "Courier 20 bold")
            self.option_add("*TextWindow.printCommand", "lpr")
        else :
            self.option_add("*TextWindow*Text.font", "Courier 12 bold")
            self.option_add("*TextWindow*Entry.font", "Courier 12 bold")
            self.option_add("*TextWindow.printCommand", "lpr")
        #---------------------------------------------------------------------
        # main layout
        #---------------------------------------------------------------------
        self.__Component["wbut"] = None
        mbar = Frame(self, relief="raised", bd="3")
        mbar.pack(side=TOP, fill=X)
        self.__Component["mbar"]  = mbar
        #---------------------------------------------------------------------
        # text-window
        #---------------------------------------------------------------------
        text  = Text(self, wrap=NONE, undo=True)
        sybar = Scrollbar(self, orient=VERTICAL)
        sxbar = Scrollbar(self, orient=HORIZONTAL)
        text["yscrollcommand"] = sybar.set
        text["xscrollcommand"] = sxbar.set
        sybar["command"]       = text.yview
        sxbar["command"]       = text.xview
        text["height"]         = self["text_height"]
        text["width"]          = self["text_width"]
        text["background"]     = self["text_background"]
        text["foreground"]     = self["text_foreground"]
        sybar.pack(side=RIGHT, fill=Y)
        sxbar.pack(side=BOTTOM, fill=X)
        text.pack(side=TOP, fill=BOTH, expand=True)
        self.__Component["text"] = text
        #---------------------------------------------------------------------
        # menu-bar
        #---------------------------------------------------------------------
        def cfind(event, self=self):
            self.__clear_find()
        def efind(event, self=self):
            self.__entry_find()
        findframe  = Frame(mbar, relief="raised", bd="3")
        findframe.pack(side=RIGHT, fill=X)
        findbutton = Button(findframe, bd="3", text="find", width="10")
        findbutton.pack(side=RIGHT)
        findentry  = Entry(findframe, relief="sunken", bd="3")
        findentry.pack(fill=X)
        findentry["width"]=40
        findbutton["command"] = self.__entry_find
        findentry.bind("<Key>",    cfind)
        findentry.bind("<Return>", efind)
        self.__Component["findentry"]  = findentry
        self.__Component["findbutton"] = findbutton
        #---------------------------------------------------------------------
        # File, Edit menu buttons
        # highlight, undo, redo buttons
        #---------------------------------------------------------------------
        filemb = Menubutton(mbar, text="File")
        filemb.pack(side=LEFT, padx=10, pady=10)
        editmb = Menubutton(mbar, text="Edit")
        editmb.pack(side=LEFT, padx=10, pady=10)
        highlight_button = Button(mbar, text="Highlight")
        highlight_button["command"] = self.highlight_lines
        highlight_button.pack(side=LEFT, padx=10, pady=10)
        undo_button = Button(mbar, bd=3, text="undo")
        undo_button["command"] = self.undo
        undo_button.pack(side=LEFT, padx=10, pady=10)
        redo_button = Button(mbar, bd=3, text="redo")
        redo_button["command"] = self.redo
        redo_button.pack(side=LEFT, padx=10, pady=10)
        filemenu = Menu(filemb)
        editmenu = Menu(editmb)
        filemb["menu"] = filemenu
        editmb["menu"] = editmenu
        #---------------------------------------------------------------------
        # File, Edit menu commands
        #---------------------------------------------------------------------
        self.__wrapMode = IntVar()
        self.__wrapMode.set(0)
        def delhigh(self=self):
            self.delete_lines(highlightedflag=True)
        def delunhigh(self=self):
            self.delete_lines(highlightedflag=False)
        def shr(self=self) :
            self.shift_highlighted_lines(shift_left=False)
        def shl(self=self) :
            self.shift_highlighted_lines(shift_left=True)
        filemenu.add_command(label="read",         command=self.fileread)
        filemenu.add_command(label="save",         command=self.filesave)
        filemenu.add_command(label="save as ...",  command=self.filesaveas)
        filemenu.add_command(label="print",        command=self.tbprint)
        filemenu.add_command(label="help",         command=self.help)
        filemenu.add_command(label="quit",         command=self.__quit_cmd)
        editmenu.add_command(label="clear",        command=self.clear)
        editmenu.add_checkbutton(label= "wrap", variable=self.__wrapMode,
            command=self.wrap)
        editmenu.add_command(label="line-up",      command=self.lineup)
        editmenu.add_command(label="line-up (csv)",command=self.lineupcsv)
        editmenu.add_command(label="split-up",     command=self.splitup)
        editmenu.add_command(label="true-wrap",    command=self.truewrap)
        editmenu.add_command(label="trim lines",   command=self.trimlines)
        editmenu.add_command(label="indent highlighted lines",
            command=shr)
        editmenu.add_command(label="unindent highlighted lines",
            command=shl)
        editmenu.add_command(label="delete highlighted lines",
            command=delhigh)
        editmenu.add_command(label="delete non-highlighted lines",
            command=delunhigh)
        editmenu.add_command(label="pipe through ...",
            command=self.pipethrough)
        editmenu.add_command(label="awk  ...",
            command=self.pipethrough_awk)
        editmenu.add_command(label="sort ...",
            command=self.pipethrough_sort)
        editmenu.add_command(label="join spice continued lines",
            command=self.join_spice)
        editmenu.add_command(label="join spectre continued lines",
            command=self.join_spectre)
        editmenu.add_command(label="change highlight color",
            command=self.choose_color)
        editmenu.add_command(label="change comment character",
            command=self.choose_comment_char)
   
        text = self.__Component["text"]
        # program interface
        #text.tag_configure("prog", foreground="blue")
        #text.tag_configure("user", foreground="red")
        text.mark_set("endtext", 1.0)
        text.mark_set("begtext", "endtext")
        text.mark_set("insert", "endtext")
        text.mark_gravity("begtext", LEFT)
        text.mark_gravity("endtext", RIGHT)
        #---------------------------------------------------------------------
        # update / mainloop
        #---------------------------------------------------------------------
        text.focus()
        self.update()
        if self.__toplevel:
            self.__toplevel.wm_title("twin")
        if self.__openfile :
            self.fileread(self.__openfile)
        if self["wait"] :
            self.wait()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # TextWindow user commands
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD : wait
    # PURPOSE : wait in main-loop until main window is destroyed
    #==========================================================================
    def wait(self, text=None) :
        """ wait in main-loop until main window is destroyed.

        **arguments**:

            .. option:: text (string, default=None)

                If text is specified, a button is displayed with the text
                in the button.  Clicking the button releases the application
                from the main event-loop.

        **results**:

            * If no text is displayed, then the application waits for the
              TextWindow instance to somehow be destroyed.  If text was
              specified, then the application waits until the button is
              clicked.

        """
        if self.__toplevel :
            self.__toplevel.deiconify()
        if text :
            mbar = self.__Component["mbar"]
            wbut = Button(mbar, text=text, background="gold")
            wbut.pack(side=LEFT)
            wbut["command"] = wbut.destroy
            self.__Component["wbut"] = wbut
            wbut.wait_window()
            if not self.winfo_exists() :
                exit()
        else :
            self.wait_window()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # TextWindow GUI file-menu callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD : fileread
    # PURPOSE : read file (also user method)
    #==========================================================================
    def fileread(self, file=None) :
        """ read file.

        **arguments**:

            .. option:: file (string, default=None)

                Name of a file to read and display/edit.
                If *file* is not specified, then a file dialog is used to
                find a file to read in.

        **results**:

            * Once a file name is found, and it is a valid file, then it
              is read in and displayed in the *Text* window.

        """
        if file == None :
            file = tkFileDialog.askopenfilename(
                parent = self,
                title = "file name to read?",
                initialdir = os.getcwd(),
                filetypes = (
                    ("all files", "*"),
                    ("text files", "*.txt"),
                )
            )
            if not file:
                return
        elif not os.path.isfile(file):
            print "file " + file + " doesn't exist"
            return
        self.__savefile = file
        f = open(file, "r")
        self.clear()
        lines = f.read()
        lines = string.strip(lines, "\n")
        self.enter(lines)
        f.close()
    #==========================================================================
    # METHOD : filesaveas
    # PURPOSE : save file using filesave dialog (also user method)
    #==========================================================================
    def filesaveas(self) :
        """ save file using filesave dialog.

        **arguments**:

            .. option:: file (string, default=None)

                Name of a file to save the *Text* contents to.
                If *file* is not specified, then a file dialog is used to
                find a file name to create or over-write.

        **results**:

            * Once a file name is found, and it is a valid file, then it
              is written or over-written with the contents of the *Text* 
              window.

        """
        savefile = tkFileDialog.asksaveasfilename(
            parent = self,
            title = "file name to save?",
            initialfile = self.__savefile,
            initialdir = os.getcwd(),
            filetypes = (
                ("all files", "*"),
                ("text files", "*.txt"),
            )
        )
        if not savefile :
            return
        self.__savefile = savefile
        self.filesave()
    #==========================================================================
    # METHOD : filesave
    # PURPOSE : save file using current file name (also user method)
    #==========================================================================
    def filesave(self) :
        """ save file using current file name.

        **results**:

            * Save the contents of the *Text* window to the current
              file name, which is established when a file is read-in,
              or a file is specified to write to.

        """
        print "writing " + self.__savefile
        f=open(self.__savefile, "w")
        lines=self.getall()
        lines=lines.encode("ascii", "replace")
        f.write(lines)
        f.close()
    #==========================================================================
    # METHOD : tbprint
    # PURPOSE : print (also user method)
    #==========================================================================
    def tbprint(self) :
        """ print.

            **results**:

                * print *Text* window contents, using the current print command.
        """
        try :
            #rintCommand = "lpr"
            printCommand = self.option_get("printCommand", "Command")
        except :
            print "print command not defined"
            return
        file = "textwindow.txt"
        f = open(file, "w")
        lines=self.getall()
        lines=lines.encode("ascii", "replace")
        f.write(lines)
        f.close()
        cmd = printCommand + " " + file
        subprocess.Popen(string.split(cmd))
    #==========================================================================
    # METHOD : __quit_cmd
    # PURPOSE : destroy window
    #==========================================================================
    def __quit_cmd(self) :
        self.quit()
        wbut = self.__Component["wbut"]
        if wbut :
            wbut.destroy()
        if self["destroy"] :
            self.__del__()
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # TextWindow GUI edit-menu callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD : clear
    # PURPOSE : delete all text (also user command)
    #==========================================================================
    def clear(self) :
        """ delete all text.

        **results**:

            * The *Text* window is cleared of all text.

        """
        text = self.__Component["text"]
        text.delete(1.0, END)
        text.mark_set("begtext", "endtext")
        text.mark_set("insert", "endtext")
    #==========================================================================
    # METHOD : enter
    # PURPOSE : enter text (also user command)
    #==========================================================================
    def enter(self, input) :
        """ enter text.

        **arguments**:

            .. option:: input (string, default=None)

                Lines of text to enter into the *Text* window.

        **results**:

            * The input lines are entered into the *Text* window.

        """
        text = self.__Component["text"]
        text.insert("endtext", input, "prog")
        text.mark_set("begtext", "endtext")
        text.mark_set("insert", "endtext")
        self.update()
    #==========================================================================
    # METHOD : get
    # PURPOSE : return text from begtext to endtext marks (also user command)
    #==========================================================================
    def get(self) :
        """ return text from begtext to endtext marks.

        **results**:

            * Return text between begtext and endtext marks, including
              newlines.  The begtext and endtext marks are
              established by (text) highlighting a region of the *Text*
              window contents.

        """
        text = self.__Component["text"]
        input = text.get("begtext", "endtext")
        text.mark_set("begtext", "endtext")
        text.mark_set("insert",  "endtext")
        return(input)
    #==========================================================================
    # METHOD : getall
    # PURPOSE : return all text (also user command)
    #==========================================================================
    def getall(self) :
        """ return all text.

        **results**:

            * Return all of the *Text* window contents, including newlines.

        """
        text = self.__Component["text"]
        return(text.get(1.0, END))
    #==========================================================================
    # METHOD : getlinelist
    # PURPOSE : return lines of text as a list (also user command)
    #==========================================================================
    def getlinelist(self) :
        """ return lines of text as a list.

        **results**:

            * Return all of the *Text* window contents, split into a list
              by newlines.

        """
        lines = self.getall()
        lines = string.split(lines, "\n")
        lines.pop(-1)
        return(lines)
    #==========================================================================
    # METHOD : choose_color
    # PURPOSE : set highlight color using color dialog (also user command)
    #==========================================================================
    def choose_color(self) :
        """ set highlight color using color dialog.

        **results**:

            * Display Tk color dialog (depends on the system)

            * Set the color which is to be used to highlight lines of
              the *Text* window.

        """
        color=self.__highlight_color
        cx, cy = tkColorChooser.askcolor(
            parent=self, title="color", color=color
        )
        if not cy is None :
            print "color = ", cy
            self.__highlight_color = str(cy)
    #==========================================================================
    # METHOD : choose_comment_char
    # PURPOSE : set comment character (for lineup command)
    #==========================================================================
    def choose_comment_char(self) :
        """ set comment character.

        **results**:

            * Display dialog to choose a comment character.

            * Type in the comment character, which is used by some of the
              Edit tools.

        """
        c = tkSimpleDialog.askstring(
            parent=self, title="comment character",
            prompt="comment character", initialvalue=self.__comment_char
        )
        if not c is None :
            self.__comment_char = c
    #==========================================================================
    # METHOD : wrap
    # PURPOSE : wrap text (also user command)
    #==========================================================================
    def wrap(self) :
        """ wrap text.

        **results**:

            * The *Text* window wrap display is toggled.  The actual contents
              of the *Text* window are not changed.

        """
        text = self.__Component["text"]
        if self.__wrapMode.get() == 0 :
            text["wrap"] = NONE
        else :
            text["wrap"] = CHAR
    #==========================================================================
    # METHOD : trimlines
    # PURPOSE : trim lines of text (also user command)
    #==========================================================================
    def trimlines(self) :
        """ trim lines of text.

        """
        olines = []
        for line in self.getlinelist() :
            line = string.strip(line)
            olines.append(line)
        self.clear()
        self.enter(string.join(olines, "\n"))
    #==========================================================================
    # METHOD : lineup
    # PURPOSE : line up all un-commented lines (also user command)
    #==========================================================================
    def lineup(self) :
        """ line up all un-commented lines.

        """
        lines = self.getlinelist()
        Col = {}
        for line in lines :
            if TextWindow.is_commented(line, self.__comment_char) :
                continue
            for i, word in enumerate(string.split(line)) :
                x = len(word)
                if not i in Col or x > Col[i] :
                    Col[i] = x
        olines = []
        for line in lines :
            if TextWindow.is_commented(line, self.__comment_char) :
                olines.append(line)
                continue
            oline = []
            for i, word in enumerate(string.split(line)) :
                n = Col[i] - len(word)
                pad = " " * n
                oline.append(word + pad)
            olines.append(string.join(oline))
        self.clear()
        self.enter(string.join(olines, "\n"))
    #==========================================================================
    # METHOD : lineupcsv
    # PURPOSE : line up all un-commented lines (also user command) for csv
    #==========================================================================
    def lineupcsv(self) :
        """ line up all un-commented lines.

        """
        lines = self.getlinelist()
        nlines = []
        for line in lines :
            line=re.sub(" ",  "@_SPC_@", line)
            line=re.sub("\t", "@_TAB_@", line)
            line=re.sub(",,", ",_,", line)
            line=re.sub(",", " ", line)
            nlines.append(line)
        Col = {}
        for line in nlines :
            if TextWindow.is_commented(line, self.__comment_char) :
                continue
            for i, word in enumerate(string.split(line)) :
                word=re.sub("@_SPC_@", " ",  word)
                word=re.sub("@_TAB_@", "\t", word)
                x = len(word)
                if not i in Col or x > Col[i] :
                    Col[i] = x
        olines = []
        for line in nlines :
            if TextWindow.is_commented(line, self.__comment_char) :
                olines.append(line)
                continue
            oline = []
            for i, word in enumerate(string.split(line)) :
                word=re.sub("@_SPC_@", " ",  word)
                word=re.sub("@_TAB_@", "\t", word)
                n = Col[i] - len(word)
                pad = " " * n
                oline.append(word + pad)
            olines.append(string.join(oline))
        self.clear()
        self.enter(string.join(olines, "\n"))
    #==========================================================================
    # METHOD : pipethrough
    # PURPOSE : pipe text lines through command (also user command)
    #==========================================================================
    def pipethrough(self) :
        """ pipe text lines through command.

        """
        cmd = tkSimpleDialog.askstring(
            parent=self,
            title="pipethrough", prompt="Command", initialvalue="sort -n -k 1"
        )
        if not cmd :
            return
        #----------------------------------------------------------------------
        # tokenize command for subprocess
        #----------------------------------------------------------------------
        apos = False
        toks = []
        tok  = ""
        for c in cmd :
            if c == "'" :
                apos = not apos
                if apos :
                   tok = ""
                else :
                   toks.append(tok)
                   tok = ""
            elif apos :
                tok +=c
            elif c == " " or c == "\t" :
                if len(tok) > 0 :
                   toks.append(tok)
                   tok = ""
            else :
                tok += c
        if len(tok) > 0 :
            toks.append(tok)    

        tmp = "tmp_file.txt"
        f = open(tmp, "w")
        lines=self.getall()
        lines=lines.encode("ascii", "replace")
        f.write(lines)
        f.close()
        try :
            p1 = subprocess.Popen(["cat", tmp], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(toks, stdin=p1.stdout, stdout=subprocess.PIPE)
            newtext = p2.communicate()[0]
        except subprocess.CalledProcessError, err:
            newtext = ""
            print err
        if os.path.isfile(tmp) :
            os.remove(tmp)
        self.clear()
        self.enter(newtext)
    #==========================================================================
    # METHOD : pipethrough_awk
    # PURPOSE : pipe text lines through command (also user command)
    #==========================================================================
    def pipethrough_awk(self) :
        """ pipe text lines through command.

        """
        cmd = tkSimpleDialog.askstring(
            parent=self,
            title="awk", prompt="AWK Command", initialvalue=""
        )
        if not cmd :
            return
        toks = []
        toks.append("awk")
        toks.append(cmd)
        tmp = "tmp_file.txt"
        f = open(tmp, "w")
        lines=self.getall()
        lines=lines.encode("ascii", "replace")
        f.write(lines)
        f.close()
        try :
            p1 = subprocess.Popen(["cat", tmp], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(toks, stdin=p1.stdout, stdout=subprocess.PIPE)
            newtext = p2.communicate()[0]
        except subprocess.CalledProcessError, err:
            newtext = ""
            print err
        if os.path.isfile(tmp) :
            os.remove(tmp)
        self.clear()
        self.enter(newtext)
    #==========================================================================
    # METHOD : __spice_sort
    # PURPOSE : sort fields with spice scale factors
    #==========================================================================
    def __spice_sort(self, line1, line2, ipos1, ipos2) :
        x1 = string.split(line1)
        x2 = string.split(line2)
        i1 = ipos1-1
        i2 = ipos2+1
        for y1,y2 in zip(x1[i1:i2],x2[i1:i2]) :
            u1 = float(decida.spice_value(y1))
            u2 = float(decida.spice_value(y2))
            if   u1 > u2 :
               return 1
            elif u1 < u2 :
               return -1
        return 0
    #==========================================================================
    # METHOD : pipethrough_sort
    # PURPOSE : pipe text lines through command (also user command)
    #==========================================================================
    def pipethrough_sort(self) :
        """ pipe text lines through command.

        """
        guititle = "sort parameters"
        guispecs = [
            ["check", "sort parameters", [
                 ["num", "numeric sort",  True],
                 ["rev", "reverse sort",  False],
                 ["spice", "use spice scale factors",  False],
            ]],
            ["entry", "sort positions",  [
                 ["pos1", "beginning position", "1"],
                 ["pos2", "ending position", ""],
            ]],
        ]
        sd = SelectionDialog(self, title=guititle, guispecs=guispecs)
        V=sd.go()
        if not V["ACCEPT"] :
            return
        pos1  = string.strip(V["pos1"])
        pos2  = string.strip(V["pos2"])
        num   = V["num"]
        rev   = V["rev"]
        spice = V["spice"]
        if len(pos1) == 0 :
            pos1 = "1"
        if len(pos2) == 0 :
            pos2 = pos1
        if spice :
            ipos1 = int(pos1)
            ipos2 = int(pos2)
            lines = self.getlinelist()
            def ssort(line1, line2, self=self, ipos1=ipos1, ipos2=ipos2) :
                return self.__spice_sort(line1, line2, ipos1, ipos2)
            lines.sort(cmp=ssort)
            if rev:
                lines.reverse()
            self.clear()
            self.enter(string.join(lines, "\n") + "\n")
            return
        toks = []
        toks.append("sort")
        if num :
            toks.append("-n")
        if rev :
            toks.append("-r")
        toks.append("-k")
        toks.append("%s,%s" % (pos1, pos2))

        tmp = "tmp_file.txt"
        f = open(tmp, "w")
        lines=self.getall()
        lines=lines.encode("ascii", "replace")
        f.write(lines)
        f.close()
        try :
            p1 = subprocess.Popen(["cat", tmp], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(toks, stdin=p1.stdout, stdout=subprocess.PIPE)
            newtext = p2.communicate()[0]
        except subprocess.CalledProcessError, err:
            newtext = ""
            print err
        if os.path.isfile(tmp) :
            os.remove(tmp)
        self.clear()
        self.enter(newtext)
    #==========================================================================
    # METHOD : join_spice
    # PURPOSE : join spice netlist continued lines
    #==========================================================================
    def join_spice(self) :
        """ join spice netlist continued lines.

        """
        lines = self.getall()
        lines = re.sub("\r", " ", lines)
        lines = re.sub("\n *\\+", " ", lines)
        self.clear()
        self.enter(lines)
    #==========================================================================
    # METHOD : join_spectre
    # PURPOSE : join spectre netlist continued lines
    #==========================================================================
    def join_spectre(self) :
        """ join spectre netlist continued lines.
        """
        xlines = []
        xline = ""
        lines = self.getall()
        lines = string.split(lines, "\n")
        for line in lines :
            line = re.sub("\r", "", line)
            line = re.sub("\n", "", line)
            line = re.sub("\t", " ", line)
            line = string.strip(line)
            if len(line) == 0:
                if len(xline) > 0:
                    xline = re.sub("[\t ]+", " ", xline)
                    xlines.append(xline)
                xline = ""
            elif line[-1] == "\\" :
                xline += line[0:-1]
            else :
                xline += line
                xline = re.sub("[\t ]+", " ", xline)
                xlines.append(xline)
                xline = ""
        if len(xline) > 0:
            xline = re.sub("[\t ]+", " ", xline)
            xlines.append(xline)
        self.clear()
        self.enter(string.join(xlines, "\n"))
    #==========================================================================
    # METHOD : splitup
    # PURPOSE : split up text lines (also user command)
    #==========================================================================
    def splitup(self) :
        """ split up text lines.

        """
        text = self.__Component["text"]
        #--------------------------------------------------------------------
        # get place to split: position of insert cursor
        #--------------------------------------------------------------------
        line, col = string.split(text.index("insert"), ".")
        firstline = string.atoi(line)
        place     = string.atoi(col)
        if place < 1 :
             print "insert cursor must be to the right of text length for split"
             print "It cannot be at left-most position in the line!"
             return
        #--------------------------------------------------------------------
        # eventually: split-up only highlighted lines!
        #--------------------------------------------------------------------
        lines = self.getlinelist()
        nlines = len(lines)
        Line = {}
        for iline, line in enumerate(lines) :
            nline = iline + 1
            n = min(place, len(line))
            if nline < firstline :
                Line[nline] = [line]
            else :
                Line[nline] = [line[0:n], line[n:]]
        olines = []
        for part in [0, 1] :
            for nline in range(1, nlines+1) :
                if part <= len(Line[nline]) - 1 :
                    olines.append(Line[nline][part])
            olines.append("_" * 72)
        self.clear()
        self.enter(string.join(olines, "\n"))
    #==========================================================================
    # METHOD : truewrap
    # PURPOSE : wrap text lines by modifying text (also user command)
    #==========================================================================
    def truewrap(self) :
        """ wrap text lines by modifying text.

        **results**:

            * The contents of the *Text* display are modified such that
              each line of text is limited to 80 characters or less.

        """
        #-------------------------------------------------------------------
        # eventually: truewrap only highlighted lines!
        #-------------------------------------------------------------------
        lines = self.getlinelist()
        linelength = self.__truewrap_linelength
        olines = []
        for line in lines :
            n = len(line)
            if n == 0 or n <= linelength :
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
                        olines.append(line[0:linelength])
                        line = line[linelength:]
                    n = len(line)
                if n > 0 :
                    olines.append(line)
        self.clear()
        self.enter(string.join(olines, "\n"))
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # TextWindow GUI highlight callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD : highlight_clear
    # PURPOSE : clear all highlighting (also user command)
    #==========================================================================
    def highlight_clear(self, lineno=None) :
        """ clear highlighting.

        **arguments**:

            .. option:: lineno (int, default=None)

               line number to clear highlighting.

        **results**:

            * Clear highlighting from specified line (lineno).

        """
        text = self.__Component["text"]
        if lineno in self.__highlighted_lines :
            tag = "highlight_" + str(lineno)
            tags = text.tag_names()
            if tag in tags :
                text.tag_delete(tag)
            self.__highlighted_lines.pop(lineno)
    #==========================================================================
    # METHOD : highlight_line
    # PURPOSE : highlight a line of text (also user command)
    #==========================================================================
    def highlight_line(self, lineno) :
        """ highlight a line of text.

        **arguments**:

            .. option:: lineno (int, default=None)

                line number to highlight.

        **results**:

            * Highlight specified line.

        """
        text = self.__Component["text"]
        color = self.__highlight_color
        tag = "highlight_" + str(lineno)
        if not lineno in self.__highlighted_lines :
            self.__highlighted_lines[lineno] = 1
            ef  = str(lineno) + ".0"
            el  = str(lineno) + ".end"
            text.tag_add(tag, ef, el)
        text.tag_configure(tag, background=color)
    #==========================================================================
    # METHOD : highlight_lines
    # PURPOSE : highlight lines of text (also user command)
    #==========================================================================
    def highlight_lines(self) :
        """ highlight lines of text.

        **results**:

            * Highlight lines where text is selected, or insert cursor
              is placed.

        """
        text = self.__Component["text"]
        ranges = text.tag_ranges("sel")
        if len(ranges) == 2 :
            if True or sys.platform == "darwin" :
                sline1 = ranges[0].string
                sline2 = ranges[1].string
            else :
                sline1 = ranges[0]
                sline2 = ranges[1]
            line1, col1 = TextWindow.linecol(sline1)
            line2, col2 = TextWindow.linecol(sline2)
            for lineno in range(line1, line2+1) :
                if lineno in self.__highlighted_lines :
                    self.highlight_clear(lineno)
                else :
                    self.highlight_line(lineno)
        else :
            insert_place = text.index("insert")
            lineno, col = TextWindow.linecol(insert_place)
            if lineno in self.__highlighted_lines :
                self.highlight_clear(lineno)
            else :
                self.highlight_line(lineno)
    #==========================================================================
    # METHOD : gethighlightedlinelist
    # PURPOSE : get highlighted lines of text as list (also user command)
    #==========================================================================
    def gethighlightedlinelist(self) :
        """ get highlighted lines of text as a list.

        **results**:

            * Return list of lines of text which are highlighted.

        """
        text = self.__Component["text"]
        lines = []
        highlightedlines = self.__highlighted_lines
        highlightedlines.sort()
        for lineno in highlightedlines :
            ef = str(lineno) + ".0"
            el = str(lineno) + ".end"
            line = text.get(ef, ef, el)
            lines.append(line)
        print "gethighlightedlinelist", str(lines)
        return(lines)
    #==========================================================================
    # METHOD : delete_lines
    # PURPOSE : delete lines of text (also user command)
    #==========================================================================
    def delete_lines(self, highlightedflag=False) :
        """ delete lines of text.

        **arguments**:

            .. option:: highlightedflag (bool, default=False)

               If True, delete highlighted lines, else delete unhighlighted
               lines.

        **results**:

            * *Text* window lines are deleted: if highlightedflag is True,
              delete only highlighted lines, otherwise delete unhighlighted
              lines.

        """
        olines = []
        lines = self.getlinelist()
        for lineno, line in enumerate(lines) :
            if lineno+1 in self.__highlighted_lines :
                is_highlighted = 1
            else :
                is_highlighted = 0
            if highlightedflag ^ is_highlighted :
                olines.append(line)
        self.clear()
        self.enter(string.join(olines, "\n"))
    #==========================================================================
    # METHOD : shift_highlighted_lines
    # PURPOSE : shift highlighted lines right or left
    #==========================================================================
    def shift_highlighted_lines(self, shift_left=False) :
        """ shift highlighted lines right or left.

        **arguments**:

            .. option:: shift_left (bool, default=False)

                If True, shift left, otherwise shift right.

        **results**:

            * Highlighted text is shifted right or left by 4 characters.
              For left-shift, only lines that have 4 spaces to spare at the
              beginning of the line are shifted.

        """
        olines = []
        lines = self.getlinelist()
        for lineno, line in enumerate(lines) :
            if lineno+1 in self.__highlighted_lines :
                if shift_left :
                    line = re.sub("^    ", "", line)
                else :
                    line = "    " + line
            olines.append(line)
        self.clear()
        self.enter(string.join(olines, "\n"))
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # TextWindow GUI undo/redo callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD : undo
    # PURPOSE : undo last change (also user command)
    #==========================================================================
    def undo(self) :
        """ undo last change.

        **results**:

            * Last *Text* window editing change is undone.

        """
        text = self.__Component["text"]
        try :
            text.edit_undo()
        except Tkinter.TclError, err :
            print err
    #==========================================================================
    # METHOD : redo
    # PURPOSE : redo last change (also user command)
    #==========================================================================
    def redo(self) :
        """ redo last change.

        **results**:

            * Last *Text* window editing change which was undone is redone.

        """
        text = self.__Component["text"]
        try :
            text.edit_redo()
        except Tkinter.TclError, err :
            print err
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # TextWindow GUI find callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD : __entry_find
    # PURPOSE : find entrybox text
    #==========================================================================
    def __entry_find(self) :
        findentry  = self.__Component["findentry"]
        findbutton = self.__Component["findbutton"]
        texttofind = findentry.get()
        self.find(texttofind)
        findbutton.configure(text="find next")
    #==========================================================================
    # METHOD : __clear_find
    # PURPOSE : clear entrybox text
    #==========================================================================
    def __clear_find(self) :
        text       = self.__Component["text"]
        findbutton = self.__Component["findbutton"]
        text.mark_set("mfind", 1.0)
        marks = text.mark_names()
        if "found" in marks :
            text.tag_delete("found")
        findbutton.configure(text="find")
    #==========================================================================
    # METHOD : find
    # PURPOSE : find texttofind (also user command)
    #==========================================================================
    def find(self, texttofind) :
        """ find text.

        **arguments**:

            .. option:: texttofine (string)

                 Text to locate in the *Text* window.

        **results**:

            * If text is found, the *Text* window view is shifted to the
              line where the found text resides and the text is highlighted 
              in red foreground.

        """
        text = self.__Component["text"]
        marks = text.mark_names()
        tags  = text.tag_names()
        if not "mfind" in marks :
            text.mark_set("mfind", 1.0)
        find_this = text.search(texttofind, "mfind")
        if find_this != "" :
            n = len(texttofind)
            ef = str(find_this) + " + " + str(n) + " chars"
            if "found" in tags :
                text.tag_delete("found")
            text.tag_add("found", find_this, ef)
            text.tag_configure("found", foreground = "red")
            text.see(find_this)
            text.mark_set("mfind", ef)
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # TextWindow program interface methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD : procmd_return
    # PURPOSE : gather user input, send to program, enter program response
    #==========================================================================
    def __progcmd_return(self) :
        """ gather user input, send to program, enter program response.

            ** not implemented **
        """
        #set userinput  [$_text get begtext endtext]
        #set progoutput [eval $progcmd $userinput]
        #$_text insert endtext "$progoutput" prog
        #$_text insert endtext "\n$prompt"
        #$_text mark set begtext endtext
        #$_text mark set insert  endtext
        #$_text see endtext
        pass
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # TextWindow GUI help button callback method
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #--------------------------------------------------------------------------
    # METHOD  : help
    # PURPOSE : help callback (also user command)
    #--------------------------------------------------------------------------
    def help(self) :
        """ help callback.

        **results**:

            * Help FrameNotebook is displayed.

        """
        #--------------------------------------------------------------------
        # locate help directory
        #--------------------------------------------------------------------
        ok = False
        for d in sys.path :
            dir = "%s/decida/twin_help/" % (d)
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
