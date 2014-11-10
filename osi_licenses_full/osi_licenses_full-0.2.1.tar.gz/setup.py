#!/bin/env python
# -*- coding: utf8 -*-

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

version = "0.2.1"

setup(
    name="osi_licenses_full",
    version=version,
    description=("A python utility for downloading all OSI approved licenses "
        "in markdown format"),
    classifiers=[],
    keywords="osi foss markdown license",
    author="Liam Middlebrook",
    author_email="liammiddlebrook@gmail.com",
    url="https://github.com/liam-middlebrook/osi-licenses-full",
    license="MIT",
    packages=find_packages(
    ),
    scripts=[
        "distribute_setup.py",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "fuzzywuzzy",
    ],
    #TODO: Deal with entry_points
    entry_points={
    'console_scripts' : [
    'osi-licenses-full = osi_licenses_full:main'],
    },
)
