#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "versioner",
    version = read("VERSION"),
    author = "José Tomás Tocino",
    author_email = "josetomas.tocino@gmail.com",
    description = ("A very basic command-line tool and library to keep "
        "track of the version of your project."),
    license = "GPLv2",
    keywords = "version versioning tool revision mayor minor",
    url = "http://josetomastocino.com",
    packages=['versioner', 'tests'],
    scripts = ['versioner/versioner.py'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    entry_points = {
        'console_scripts': [
            'versioner = versioner:main'
        ]
    }
)