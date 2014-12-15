#!/usr/bin/env python
from distutils.core import setup

setup(
    name='idncheck',
    version='0.1.1',
    author='AJ Bowen',
    author_email='aj@gandi.net',
    url = 'https://github.com/soulshake/idncheck',
    packages=['idncheck', 'idncheck.tests'],
    license='LICENSE.txt',
    description='Returns IDN restriction level of a string.',
    keywords = ['idn']
)

