#!/usr/bin/env python

"""
Setup script for PingMeCli.
"""

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

import os

if os.path.exists('README.rst'):
    README = open('README.rst').read()
else:
    README = ""  # a placeholder, readme is generated on release
CHANGES = open('CHANGES.md').read()

setup(
    name='pingme',
    version='0.0.1',
    packages=['pingme'],
    url='https://github.com/teddy-schmitz/pingme-cli',
    license='',
    author='Teddy Schmitz',
    author_email='lted.schmitz@gmail.com',
    description='Cli for Pingme Android application.',
    entry_points={
        'console_scripts': ['pingme = pingme.pingme:main']
    },
    install_requires=open('requirements.txt').readlines(),
    long_description=(README + '\n' + CHANGES),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
    ]
)
