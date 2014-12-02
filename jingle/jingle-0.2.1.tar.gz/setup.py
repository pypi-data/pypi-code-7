#!/usr/bin/env python

import os
import sys
from glob import glob

try:
    from setuptools import setup
except ImportError:
    sys.stderr.write("Required setuptools package not found, falling back to distutils.core")
    from distutils.core import setup

# ------------------------------------------------------------------------------

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from jingle import __version__, __author__

# ------------------------------------------------------------------------------

install_requirements = [x for x in open('requirements/install.txt').read().split("\n") if x]

# ------------------------------------------------------------------------------

setup(
    name="jingle",
    version=__version__,
    description="Config files renderer based on Jinja2",
    author=__author__,
    author_email="hi@kkvlk.me",
    url="https://github.com/nimboost/jingle",
    download_url = "https://github.com/nimboost/jingle/tarball/v%s" % __version__,
    license="MIT",
    install_requires=[install_requirements],
    py_modules=['jingle'],
    scripts=['bin/jingle'],
    keywords = "config file template jinja nimboost",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
    ],
)
