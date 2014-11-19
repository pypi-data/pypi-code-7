#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import os
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

def local(path):
    return os.path.join(os.path.dirname(__file__), path)

# Extra Third-Party Libraries
sys.path.insert(1, local(".lib"))
try:
    requirement = "about>=4.0.0"

    pkg_resources.WorkingSet().require(requirement)
except pkg_resources.DistributionNotFound:
    error = """{req!r} not found; install it locally with:

    pip install --target=.lib --ignore-installed {req!r}
"""
    raise ImportError(error.format(req=requirement))
import about

# This Package
sys.path.insert(1, local(""))
import logfile

# ------------------------------------------------------------------------------

info = dict(
  metadata     = about.get_metadata(logfile),
  code         = dict(packages=setuptools.find_packages()),
  data         = dict(package_data={"logfile": ["README.md"]}),
  requirements = {},
  scripts      = {},
  commands     = {},
  plugins      = {},
  tests        = dict(test_suite="test.suite"),
)

if __name__ == "__main__":
    kwargs = {k:v for dct in info.values() for (k,v) in dct.items()}
    setuptools.setup(**kwargs)

