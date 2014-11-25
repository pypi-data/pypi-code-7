#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
import gunny

description = "Python package for executing commands by following a directed graph"

long_description = \
"""
gunny is a Python package for assigning commands to directed graph nodes and asynchronously executing them in order
"""

setup(
    name='gunny',
    description=description,
    long_description=long_description,
    version=gunny.__version__,
    license='BSD',
    author='Raymond Tyler Wall',
    author_email='mail@rtwall.ca',
    maintainer='Raymond Tyler Wall',
    maintainer_email='mail@rtwall.ca',
    url='https://github.com/rtwall/gunny/',
    download_url='https://pypi.python.org/pypi/gunny/',
    packages=['gunny'],
    keywords=['graph', 'network', 'subprocess', 'wrapper', 'external', 'command'],
    platforms = ['Linux','Mac OSX','Windows','Unix'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Shells',
    ],
    install_requires=[
        'sarge',
        'networkx',
        'future'
    ]
)
