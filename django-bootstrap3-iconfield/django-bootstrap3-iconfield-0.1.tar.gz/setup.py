#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = __import__("bootstrap3-iconfield").__version__

install_requires = [
    'django>=1.4.1',
    'django-bootstrap3'
]

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-bootstrap3-iconfield',
    version=VERSION,
    packages=['bootstrap3-iconfield'],
    include_package_data=True,
    license="Apache License 2.0",
    description='Renderers to show icons in the input fields for the django-bootstrap3 project from dyve: https://github.com/dyve/django-bootstrap3.',
    long_description=README,
    url='https://github.com/ALibrada/django-bootstrap3-iconfield',
    author='Antonio Librada',
    author_email='antoniolibrada@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Environment :: Web Environment',
        'Framework :: Django'
    ],
)
