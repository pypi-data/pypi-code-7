#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

LONG_DESCRIPTION = open('README.rst').read()
VERSION = '0.1.0'

setup(
    name='splitta',
    version=VERSION,
    url='https://github.com/hinstitute/splitta',
    download_url='https://github.com/hinstitute/splitta/tarball/' +
        VERSION,
    license='(c) 2009 Dan Gillick',
    author='Dan Gillick',
    author_email='dgillick@cs.berkeley.edu',
    description='API for the StoryPilot platform.',
    long_description=LONG_DESCRIPTION,
    packages=['splitta'],
    include_package_data=True,
    keywords=['splitta', 'setence bounadry detection', 'sbd']
)
