#!/usr/bin/env python

# Copyright 2011-2014 Arthur Noel
#
# This file is part of Yanc.
#
# Yanc is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Yanc is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Yanc. If not, see <http://www.gnu.org/licenses/>.

import os

from setuptools import setup
from setuptools.command import test

# monkey patch test command to make nose work with `setup.py test`
# see: http://fgimian.github.io/blog/2014/04/27/running-nose-tests-with-plugins-using-the-python-setuptools-test-command/
test._test = test.test


class NoseTestCommand(test._test):

    user_options = test._test.user_options + [
        ("args=", "a", "Arguments to pass to nose"),
    ]

    def initialize_options(self):
        test._test.initialize_options(self)
        self.args = None

    def finalize_options(self):
        test._test.finalize_options(self)
        self.args = self.args and self.args.strip().split() or []
        self.test_suite = True

    def run_tests(self):
        import nose
        nose.run_exit(argv=["nosetests"] + self.args)

test.test = NoseTestCommand

setup(
    name="yanc",
    version="0.3.3",
    description="Yet another nose colorer",
    long_description=open(
        os.path.join(os.path.dirname(__file__), "README.rst")).read(),
    license="GPL",
    keywords="nose color",
    author="Arthur Noel",
    author_email="arthur@0compute.net",
    url="https://github.com/0compute/yanc",
    packages=("yanc",),
    tests_require=[
        "nose",
    ],
    test_suite="nose.collector",
    entry_points = {
        "nose.plugins": ("yanc=yanc.yancplugin:YancPlugin",),
    },
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Testing",
    ],
)
