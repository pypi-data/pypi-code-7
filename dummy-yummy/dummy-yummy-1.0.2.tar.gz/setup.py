#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
import yummy

version = yummy.__version__

setup(
    name='dummy-yummy',
    version=version,
    description="""dummy-yummy is a dummy package used for testing automatic installation in virtualenvs with 3bot.""",
    long_description=open('README.md').read(),
    author='arteria GmbH',
    author_email='admin@arteria.ch',
    url='https://github.com/arteria/dummy-yummy',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    license="BSD",
    zip_safe=False, 
)
