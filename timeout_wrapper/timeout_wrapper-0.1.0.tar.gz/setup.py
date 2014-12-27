#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from setuptools import setup, find_packages


# Variables ===================================================================
changelog = open('CHANGES.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    changelog
])


# Functions ===================================================================
def allSame(s):
    return not filter(lambda x: x != s[0], s)


def hasDigit(s):
    return any(map(lambda x: x.isdigit(), s))


def getVersion(data):
    data = data.splitlines()
    return filter(
        lambda (x, y):
            len(x) == len(y) and allSame(y) and hasDigit(x) and "." in x,
        zip(data, data[1:])
    )[0][0]


# Actual setup definition =====================================================
setup(
    name='timeout_wrapper',
    version=getVersion(changelog),
    description='Timeout decorator with defaults and exceptions.',
    long_description=long_description,
    url='https://github.com/Bystroushaak/timeout_wrapper',

    author='Bystroushaak',
    author_email='bystrousak@kitakitsune.org',

    classifiers=[
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        "License :: OSI Approved :: MIT License",
    ],
    license='MIT',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=True,

    test_suite='py.test',
    tests_require=["pytest"],
    extras_require={
        "docs": [
            "sphinx",
            "sphinxcontrib-napoleon",
        ]
    },
)
