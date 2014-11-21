#!/usr/bin/env python

from ip2locale.metadata import *
from setuptools import setup, find_packages

REQUIREMENTS = [
    'requests',
]

setup(
    name=NAME,
    description=DESCRIPTION,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENCE,
    url=URL,
    packages=find_packages(exclude=['docs']),
    install_requires=REQUIREMENTS,
    scripts=['scripts/ip2locale']
)