#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import os.path
import sys

# Pip Package Manager
try:
    import pip
    import setuptools
    import pkg_resources
except ImportError:
    error = "pip is not installed, refer to <{url}> for instructions."
    raise ImportError(error.format(url="http://pip.readthedocs.org"))

# Numpy
import numpy

# PyAudio (no download available on PyPi)
try:
    pkg_resources.require("PyAudio")
except pkg_resources.DistributionNotFound:
    error = "{name} is not installed, refer to <{url}> for instructions."
    name, url = "PyAudio", "http://people.csail.mit.edu/hubert/pyaudio/"
    raise ImportError(error.format(name=name, url=url))

def srcdir(path):
    return os.path.join(os.path.dirname(__file__), path)

# Extra Third-Party Libraries (for setup only)
sys.path.insert(1, srcdir(".lib"))
try:
    setup_requires = ["about>=4.0.0"]
    require = lambda *r: pkg_resources.WorkingSet().require(*r)
    require(*setup_requires)
    import about
except pkg_resources.DistributionNotFound:
    error = """{req!r} not found; install it locally with:

    pip install --target=.lib --ignore-installed {req!r}
"""
    raise ImportError(error.format(req=" ".join(setup_requires)))
import about

# This Package
sys.path.insert(1, srcdir("audio"))
import about_io

info = dict(
  metadata     = about.get_metadata(about_io),
  code         = dict(packages=setuptools.find_packages()),
  data         = {},
  requirements = {},
  scripts      = {},
  plugins      = {},
  tests        = {},
)

if __name__ == "__main__":
    kwargs = {k:v for dct in info.values() for (k,v) in dct.items()}
    setuptools.setup(**kwargs)

