#! /usr/bin/env python

from setuptools import setup
from decimal import Decimal
import re

def linelist(text):
    """
    Returns each non-blank line in text enclosed in a list.
    """
    return [ l.strip() for l in text.strip().splitlines() if l.split() ]

    # The double-mention of l.strip() is yet another fine example of why
    # Python needs en passant aliasing.


setup(
    name='nulltype',
    version="2.0",
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Superclass for null types parallel to, but different from, None',
    long_description=open('README.rst').read(),
    url='https://bitbucket.org/jeunice/nulltype',
    py_modules=['nulltype'],
    install_requires=[],
    tests_require = ['tox', 'pytest'],
    zip_safe = True,
    keywords='null none singleton sentinel',
    classifiers=linelist("""
        Development Status :: 5 - Production/Stable
        Operating System :: OS Independent
        License :: OSI Approved :: BSD License
        Intended Audience :: Developers
        Programming Language :: Python
        Programming Language :: Python :: 2.5
        Programming Language :: Python :: 2.6
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3.2
        Programming Language :: Python :: 3.3
        Topic :: Software Development :: Libraries :: Python Modules
    """)
)
