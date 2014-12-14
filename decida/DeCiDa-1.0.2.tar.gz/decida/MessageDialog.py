################################################################################
# CLASS    : MessageDialog
# PURPOSE  : generic message dialog
# AUTHOR   : Richard Booth
# DATE     : Sat Nov  9 11:24:40 2013
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
from decida.DialogBase import DialogBase
from Tkinter import *
import string
class MessageDialog(DialogBase):
    """ generic message dialog.

        **synopsis**:

        *MessageDialog* is a generic dialog for displaying information.

        **constructor arguments**:

            .. option:: parent (Tkinter handle) (optional, default=None)

                handle of frame or other widget to pack plot in.
                if this is not specified, top-level is created.

            .. option:: message (text) (optional, default="")

                message to display

            .. option:: title (string) (optional, default="")

                title to be placed on dialog window

            .. option:: bitmap (string) (optional, default="")

                bitmap to be displayed on dialog window

    **public methods**:

    """
    #=========================================================================
    # METHOD : __init__
    # PURPOSE : constructor
    #=========================================================================
    def __init__(self, parent=None, message="", title="", bitmap="info"):
        DialogBase.__init__(self, parent=parent, title=title, bitmap=bitmap)
        self.__message = message
        self._gui()
        self.go()
    #=========================================================================
    # METHOD : _gui_middle
    # PURPOSE : gui middle section
    #=========================================================================
    def _gui_middle(self):
        top     = self._Component["top"]
        f_table = self._Component["table"]
        bf      = self._Component["but_frame"]
        message = self.__message
        #---------------------------------------------------------------------
        # middle entries
        #---------------------------------------------------------------------
        f_message = Frame(f_table, relief=FLAT, bd=3)
        f_message.pack(side=TOP, expand=True, fill=BOTH)
        m_message = Label(f_message, relief=GROOVE, bd=3, bg="GhostWhite",
            font="Courier 12 normal", text=message, anchor=W, justify=LEFT,
            padx=20, pady=20)
        m_message.pack(side=TOP, expand=True, fill=BOTH)
        m_message.bind("<MouseWheel>", self._mouse_wheel)
        m_message.bind("<Button-4>",   self._mouse_wheel)
        m_message.bind("<Button-5>",   self._mouse_wheel)
        m_message.bind("<Prior>",      self._page_key)
        m_message.bind("<Next>",       self._page_key)
        m_message.bind("<Home>",       self._page_key)
        m_message.bind("<End>",        self._page_key)
        #---------------------------------------------------------------------
        # ok button
        #---------------------------------------------------------------------
        bf_ok = Frame(bf, bd=2, relief=SUNKEN)
        bf_ok.pack(side=LEFT, expand=True, padx=3, pady=2)
        bf_ok_button = Button(bf_ok, text="ok",
            command=self.__ok)
        bf_ok_button.pack(anchor="c", expand=True, padx=3, pady=2)
        self._Component["ok"] = bf_ok_button
        #---------------------------------------------------------------------
        # key bindings
        #---------------------------------------------------------------------
        def ok_cmd(event, self=self) :
            self.__ok()
        top.bind("<Control-Key-s>",      ok_cmd)
        top.bind("<Return>",             ok_cmd)
        top.protocol('WM_DELETE_WINDOW', self.__ok)
    #=========================================================================
    # METHOD: __ok
    # PURPOSE: ok button call-back
    #=========================================================================
    def __ok(self):
        top = self._Component["top"]
        top.quit()
