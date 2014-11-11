#!/usr/bin/env python
import os
import sys

from setuptools import setup
requires = ['requests>=2.2.1']

description = '''This package provides a command line interface ElasticBox'''

if sys.version_info[:2] == (2, 6):
    # For python2.6 we have to require argparse since it
    # was not in stdlib until 2.7.
    requires.append('argparse>=1.1')

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = description

setup_options = dict(
    name='ebcli',
    version='3.0.2',
    description='Command Line tool for ElasticBox.',
    long_description=long_description,
    author='ElasticBox',
    author_email='support@elasticbox.com',
    url='http://elasticbox.com',
    scripts=['eb', 'README.rst'],
    py_modules=['ebcli'],
    install_requires=['requires', 'keyring', 'requests'],
    license="Apache License 2.0",
    classifiers=(
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)

setup(**setup_options)
