#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# GuessIt - A library for guessing information from filenames
# Copyright (c) 2014 Nicolas Wack <wackou@gmail.com>
#
# GuessIt is free software; you can redistribute it and/or modify it under
# the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# GuessIt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.
#
# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import absolute_import, division, print_function, unicode_literals

from guessit.test.guessittest import *
import guessit
import guessit.hash_ed2k
import unittest
import doctest


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(guessit))
    tests.addTests(doctest.DocTestSuite(guessit.date))
    tests.addTests(doctest.DocTestSuite(guessit.fileutils))
    tests.addTests(doctest.DocTestSuite(guessit.guess))
    tests.addTests(doctest.DocTestSuite(guessit.hash_ed2k))
    tests.addTests(doctest.DocTestSuite(guessit.language))
    tests.addTests(doctest.DocTestSuite(guessit.matchtree))
    tests.addTests(doctest.DocTestSuite(guessit.textutils))
    return tests

suite = unittest.TestSuite()
load_tests(None, suite, None)

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
