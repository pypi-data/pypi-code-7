#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="fmio",
    version="1.0-beta",
    description="Fast streaming I/O of numeric matrices",
    author="Cory Giles",
    author_email="mail@corygil.es",
    url="http://bitbucket.org/gilesc/fmio",
    packages=find_packages(),
    install_requires=[
        "numpy", "pandas"
    ],
    entry_points={
        "console_scripts": ["fmio = fmio:main"]
    }
)
