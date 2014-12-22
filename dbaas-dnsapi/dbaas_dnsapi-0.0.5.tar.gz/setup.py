#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='dbaas_dnsapi',
    version='0.0.5',
    description='Integration between DBAAS and DNSAPI',
    long_description=readme + '\n\n' + history,
    author='Ricardo Dias',
    author_email='ricardo@ricardodias.org',
    url='https://github.com/globocom/dbaas-dnsapi',
    packages=[
        'dbaas_dnsapi',
    ],
    package_dir={'dbaas_dnsapi':
                 'dbaas_dnsapi'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='dbaas_dnsapi',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
