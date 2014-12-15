#!/usr/bin/env python

from setuptools import setup

setup(
    author = 'Nigel Kersten',
    author_email = 'nigelk@google.com',
    description = 'Python wrappers for Mac OS X DirectoryService functions.',
    install_requires = ['pyobjc-core', 'pyobjc'],
    name = 'pymacds',
    packages = ['pymacds'],
    url = 'https://github.com/tarak/pymacds',
    version = __import__('pymacds').__version__,
)
