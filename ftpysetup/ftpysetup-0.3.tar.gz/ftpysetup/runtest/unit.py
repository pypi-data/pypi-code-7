#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""Setuptools command to execute unit tests."""
__author__ = ('Lance Finn Helsten',)
__version__ = '0.3'
__copyright__ = """Copyright (C) 2014 Lance Helsten"""
__docformat__ = "reStructuredText en"
__license__ = """
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""


from .testbase import TestBase

__all__ = ['UnitTestRunner']


class UnitTestRunner(TestBase):
    description = "Run all unit tests on the system."
    user_options = [
        ("suite=", "s", "Run specific test suite [default: all tests]."),
        ("debug=", "d", "Debug a specific test with preset breakpoints."),
        ("coverage", "c", "Turn on code coverage for the tests."),
        ("bSetup", None, "Add a breakpoint in setUp for debug."),
        ("bTeardown", None, "Add a breakpoint in tearDown for debug."),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.test_type = "unit"
        self.suite_name = 'UnitTestSuite'

