#!/usr/bin/env python
from setuptools import setup

setup(
    name="varlet",
    version='0.0.3',
    author='Matt Johnson',
    author_email='mdj2@pdx.edu',
    description="Interactive prompt for variables that should be set at runtime",
    packages=['varlet'],
    zip_safe=False,
    classifiers=[
        'Framework :: Django',
    ],
    install_requires=[
        'pyyaml',
    ],
)
