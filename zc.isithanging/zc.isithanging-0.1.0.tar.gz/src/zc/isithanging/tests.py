##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from zope.testing import setupstack
from zope.testing.renormalizing import OutputChecker
import doctest
import mock
import re
import threading
import time
import unittest

def create_blocker():
    event = threading.Event()
    def f(*args, **kw):
        event.wait()
        return args, kw
    return event, f

def setup(test):
    globs = test.globs
    globs['timetime'] = 1416149309.1
    def time_time():
        globs['timetime'] += .1
        return globs['timetime']
    setupstack.context_manager(
        test, mock.patch("time.time", side_effect=time_time))


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.rst',
            setUp=setup, tearDown=setupstack.tearDown,
            checker=OutputChecker([
                (re.compile('at 0x[0-9a-f]+'), 'at <SOME ADDRESS>'),
                ]))
        ))

