#!/usr/bin/env python
""" setup.py for goulash
"""

from setuptools import setup
from goulash import __version__

setup(
    name         = 'goulash',
    version      = __version__,
    description  = 'toolbox, random shared stuff from my other projects',
    author       = 'mattvonrocketstein',
    author_email = '$author@gmail',
    url          = 'http://github.com/mattvonrocketstein/goulash',
    download_url = 'https://github.com/mattvonrocketstein/goulash/tarball/pypi',
    packages     = ['goulash'],
    keywords     = ['goulash']
    )
