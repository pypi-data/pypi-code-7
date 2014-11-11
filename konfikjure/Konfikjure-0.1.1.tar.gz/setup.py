#!/usr/bin/env python
# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of Konfikjure.
# See the file 'docs/LICENSE.txt' for copying permission.

from setuptools import setup


setup(
    name='Konfikjure',
    version='0.1.1',
    author='Jurriaan Bremer',
    author_email='jurriaanbremer@gmail.com',
    packages=[
        'konfikjure',
    ],
    scripts=[
        'bin/konfikjure',
    ],
    license='GPLv3',
    description='Command-line based configuration utility',
)
