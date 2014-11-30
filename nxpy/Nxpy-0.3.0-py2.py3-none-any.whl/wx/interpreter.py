# nxpy.wx package ------------------------------------------------------------

# Copyright Nicola Musatti 2008 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Interactive program driver - wxPython version.

An alternative implementation of *command.interpreter.Interpreter* for use with wxPython 
applications, as the default one is not compatible with wxPython's application loop.

"""

from __future__ import absolute_import

import wx

import nxpy.command.interpreter


class Popen(object):
    r"""A simple wxPython based, Popen-like object."""
    def __init__(self, cmd):
        self.process = wx.Process(None)
        self.process.Redirect();
        wx.Execute(cmd, wx.EXEC_ASYNC, self.process)

    def send(self, data):
        self.process.GetOutputStream().write(data)

    def recv(self):
        stream = self.process.GetInputStream()
        if stream.CanRead():
            return stream.read()
        return ""

    def recv_err(self):
        stream = self.process.GetErrorStream()
        if stream.CanRead():
            return stream.read()
        return ""


class Interpreter(nxpy.command.interpreter.BaseInterpreter):
    r"""A command interpreter suitable for use in wxPython based applications."""
    def __init__(self, cmd):
        super(Interpreter, self).__init__(Popen(cmd))
