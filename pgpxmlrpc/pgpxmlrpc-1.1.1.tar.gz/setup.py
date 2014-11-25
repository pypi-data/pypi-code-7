#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

__version__ = '1.1.1'


setup (
    name = 'pgpxmlrpc',
    description = 'PGP-encrypted transport for XML-RPC protocol',
    long_description = 'This module provides PGP-encrypted transport for XML-RPC protocol',
    license = 'LGPLv3',
    version = __version__,
    author = 'Ruslan V. Uss',
    author_email = 'unclerus@gmail.com',
    maintainer = 'Ruslan V. Uss',
    maintainer_email = 'unclerus@gmail.com',
    py_modules = ['pgpxmlrpc'],
    platforms = 'No particular restrictions',
    url = 'https://github.com/UncleRus/pgpxmlrpc',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires = ['regnupg >= 0.3.4']
)
