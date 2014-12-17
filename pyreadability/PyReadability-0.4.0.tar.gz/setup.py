#!/usr/bin/env python
from setuptools import setup, find_packages
import sys


def _str_to_version_tuple(version):
    return tuple([int(i) for i in version.split('.')])


lxml_requirement = "lxml"
if sys.platform == 'darwin':
    import platform
    # Solve bad case of comparison like 10.9 v.s. 10.10.1
    mac_ver = _str_to_version_tuple(platform.mac_ver()[0])
    cutoff_ver= _str_to_version_tuple('10.9')
    if mac_ver < cutoff_ver:
        print("Using lxml<2.4")
        lxml_requirement = "lxml<2.4"

setup(
    name="PyReadability",
    version="0.4.0",
    author="Yuri Baburov",
    author_email="burchik@gmail.com",
    description="fast python port of arc90's readability tool",
    test_suite = "tests.test_article_only",
    long_description=open("README").read(),
    license="Apache License 2.0",
    url="http://github.com/hyperlinkapp/python-readability",
    packages=['readability'],
    install_requires=[
        "chardet",
        "cssselect",
        lxml_requirement
        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
)
