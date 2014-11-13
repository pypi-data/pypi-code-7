#!/usr/bin/env python
__author__ = 'Ruben Nielsen'

from setuptools import setup


setup(
    name='backup2',
    version='0.0.2.dev2',
    description='Tools for creating a backup suite',
    author='Ruben Nielsen',
    author_email='nielsen.ruben@gmail.com',
    packages=['backup2'],
    keywords=['backup', 'cli', 'commandline'],
    test_suite="backup2.tests",
    install_requires=[
        'pycrypto==2.6.1',
    ],
)
