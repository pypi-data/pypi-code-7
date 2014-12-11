#!/usr/bin/env python

import os.path
import distutils.core

import vectortile

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
    version=vectortile.__version__,
    author=vectortile.__author__,
    author_email=vectortile.__author_email__,
    url=vectortile.__source__,
    license=vectortile.__license__
)
