#!/usr/bin/env python
from setuptools import setup

setup(
    name='sydbank-exporter',
    version='0.1.0',
    description='Create a CSV file that can be read by Sydbank',
    author='Joshua Karjala-Svendsen',
    author_email='joshua@founders.as',
    url='https://github.com/joshuakarjala/sydbank-exporter',
    packages=['sydbank_exporter'],
    include_package_data=True,
    install_requires=['nose']
)
