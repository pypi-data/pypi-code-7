#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from os.path import abspath, dirname, join

# get setup directory abspath
_path = dirname(abspath(__file__))

# get long description
with open(join(_path, 'README')) as f:
    desc = f.read()

setup(
    name="b3j0f.utils",
    version="0.7.7",
    packages=find_packages(exclude=['test.*', '*.test.*']),
    author="b3j0f",
    author_email="jlabejof@yahoo.fr",
    description="b3j0f utils",
    long_description=desc,
    include_package_data=True,
    url='https://github.com/mrbozzo/utils/',
    license='MIT License',
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    test_suite='b3j0f'
)
