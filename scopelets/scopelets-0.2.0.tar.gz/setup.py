#!/usr/bin/env python

from setuptools import setup, find_packages
import os

requires = [
    'boto>=2.34.0'
]

setup(
    name="scopelets",
    version=open(os.path.join('scopelets', '_version')).read().strip(),
    author="Mitch Garnaat",
    author_email="mitch@scopely.com",
    description=(
        "Small Python utilities that are used in a number of other "
        "Scopely open source packages."
    ),
    license=open("LICENSE").read(),
    keywords="scopely ansible aws",
    url="https://github.com/scopely-devops/scopelets",
    packages=find_packages(exclude=['tests*']),
    package_data={'scopelets': ['_version'],
                  '': ['LICENSE']},
    package_dir={'scopelets': 'scopelets'},
    install_requires=requires,
    classifiers=[
        "Topic :: Utilities",
    ],
)
