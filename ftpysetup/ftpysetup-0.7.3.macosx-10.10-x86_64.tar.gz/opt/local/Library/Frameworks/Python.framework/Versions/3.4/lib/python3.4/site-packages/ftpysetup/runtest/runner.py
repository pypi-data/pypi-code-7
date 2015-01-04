#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""Setuptools command to execute all tests. This is useful for continuous
integration systems."""
__author__ = ('Lance Finn Helsten',)
__version__ = '0.7.3'
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

import sys
import setuptools

__all__ = ['TestRunner']


class TestRunner(setuptools.Command):
    description = "Run all unit and acceptance tests on the system."
    user_options = [
        ("suite=", "s", "Run specific test suite [default: all tests]."),
        ("level=", "l", "Test suite level to run: smoke, sanity, or shakedown."),
        ("debug=", "d", "Debug a specific test with preset breakpoints."),
        ("coverage", "c", "Turn on code coverage for the tests."),
        ("bSetup", None, "Add a breakpoint in setUp for debug."),
        ("bTeardown", None, "Add a breakpoint in tearDown for debug."),
    ]

    def initialize_options(self):
        self.suite = []
        self.level = "sanity"
        self.debug = None
        self.coverage = False
        self.bSetup = False
        self.bTeardown = False

    def finalize_options(self):
        if self.suite is None:
            raise ValueError("suite must be set.")

    def run(self):
        self.reinitialize_command('test_unit',
                                  suite=self.suite,
                                  debug=self.debug,
                                  coverage=self.coverage,
                                  bSetup=self.bSetup,
                                  bTeardown=self.bTeardown)
        self.run_command('test_unit')

        self.reinitialize_command('test_accept',
                                  suite=self.suite,
                                  level=self.level,
                                  debug=self.debug,
                                  coverage=self.coverage,
                                  bSetup=self.bSetup,
                                  bTeardown=self.bTeardown)
        self.run_command('test_accept')

