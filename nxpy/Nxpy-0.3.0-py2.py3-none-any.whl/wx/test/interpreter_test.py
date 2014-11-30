# nxpy.wx package ------------------------------------------------------------

# Copyright Nicola Musatti 2008 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

from __future__ import absolute_import

import wx

import nxpy.wx.interpreter


_app = None

class InterpreterTester(nxpy.wx.interpreter.Interpreter):
    r"""
    Test oriented Interpreter implementation.
    
    Useful for testing wxPython based command interpreters isolated from the visual infrastructure.
    """
    def __init__(self, cmd):
        global _app
        if not _app:
            _app = wx.App()
        super(InterpreterTester, self).__init__(cmd)