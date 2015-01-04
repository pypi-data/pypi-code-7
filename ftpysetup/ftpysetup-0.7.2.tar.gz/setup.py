#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#----------------------------------------------------------------------------
"""Flying Titans setuptools extensions."""
__author__ = ('Lance Finn Helsten',)
__version__ = '0.7.2'
__copyright__ = """Copyright (C) 2014 Lance Finn Helsten"""
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
import os
import setuptools
#from ftpysetup.website import WebDistribution

setuptools.setup(
#    distclass=WebDistribution,
    name = "ftpysetup",
    version = __version__,
    author = 'Lance Finn Helsten',
    author_email = 'lanhel@flyingtitans.com',
    description = __doc__,
    long_description = open('README.rst').read(),
    url = 'https://github.com/lanhel/ftpysetup',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Framework :: Setuptools Plugin',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
    ],
    entry_points = {
        "distutils.commands":[
            "test = ftpysetup.runtest.runner:TestRunner",
            "test_unit = ftpysetup.runtest.unit:UnitTestRunner",
            "test_accept = ftpysetup.runtest.accept:AcceptTestRunner",
            "upvers = ftpysetup.upvers:UpdateVersion",
            "venv = ftpysetup.venv:VirtualEnv",
            "build_website = ftpysetup.website:BuildWebsite",
        ],
    },
    packages = [
        'ftpysetup.cmdbuild',
        'ftpysetup.runtest',
        'ftpysetup.upvers',
        'ftpysetup.venv',
        'ftpysetup.website',
        'ftpysetup.website.config',
        'ftpysetup.website.example',
        'ftpysetup.website.example.css',
    ],
    package_data = {
        'ftpysetup.website.example':['*.rst'],
        'ftpysetup.website.example.css':['*.css']
    },
#    scripts = [
#    ],
#    websites = [
#        'ftpysetup/website/example'
#    ],
)




