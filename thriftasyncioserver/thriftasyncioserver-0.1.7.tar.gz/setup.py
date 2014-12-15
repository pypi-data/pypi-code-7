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
    'thrift',
]

test_requirements = [
    'thrift',
]

setup(
    name='thriftasyncioserver',
    version='0.1.7',
    description='Thrift Server using the Python 3 asyncio module',
    long_description=readme + '\n\n' + history,
    author='Thomas Bartelmess',
    author_email='tbartelmess@marketcircle.com',
    url='https://github.com/Marketcircle/thriftasyncioserver',
    dependency_links= ['git+https://github.com/Marketcircle/Thrift-Python.git'],
    packages=[
        'thriftasyncioserver',
    ],
    package_dir={'thriftasyncioserver':
                 'thriftasyncioserver'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=True,
    keywords='thriftasyncioserver',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
