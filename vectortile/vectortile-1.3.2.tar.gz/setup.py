#!/usr/bin/env python

import os.path
import distutils.core

# Don't import vectortile here, that would create loops. Just load
# this one file that doesn't import anything.

versionpy = os.path.join(os.path.split(os.path.abspath(__file__))[0], "vectortile/version.py")
version = {}
execfile(versionpy, version)

with open('README.md') as f:
    readme = f.read()

with open('requirements.txt') as f:
    requirements = [l for l in f.readlines() if l]

distutils.core.setup(
    name='vectortile',
    description="A set of classes for managing tiles of geospatial vector data",
    long_description=readme,
    packages=[
        'vectortile',
        'vectortile.tests'
    ],
    install_requires=requirements,
    version=version['__version__'],
    author=version['__author__'],
    author_email=version['__author_email__'],
    url=version['__source__'],
    license=version['__license__']
)
