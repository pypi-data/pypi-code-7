#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""Setuptools command to execute acceptance tests."""
__author__ = ('Lance Finn Helsten',)
__version__ = '0.0'
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

__all__ = ['AcceptTestRunner']


class AcceptTestRunner(TestBase):
    description = "Run all acceptance tests on the system."

    user_options = [
        ("suite=", "s", "Run specific test suite [default: all tests]."),
        ("level=", "l", "Test suite level to run: smoke, sanity, or shakedown."),
        ("debug=", "d", "Debug a specific test with preset breakpoints."),
        ("coverage", "c", "Turn on code coverage for the tests."),
        ("bSetup", None, "Add a breakpoint in setUp for debug."),
        ("bTeardown", None, "Add a breakpoint in tearDown for debug."),
    ]

    levels = {
        'smoke':'SmokeAcceptSuite',
        'sanity':'SanityAcceptSuite',
        'shakedown':'ShakedownAcceptSuite'
    }

    def initialize_options(self):
        super().initialize_options()
        self.test_type = "accept"
        self.level = "sanity"

    def finalize_options(self):
        if self.level not in self.levels.keys():
            raise DistutilsOptionError("Invalid test level: {0}".format(self.level))
        self.suite_name = self.levels[self.level]
        super().finalize_options()

