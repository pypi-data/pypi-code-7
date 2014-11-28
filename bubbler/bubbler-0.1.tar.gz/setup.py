#!/usr/bin/env python
import os
from setuptools import setup

# evil, dirty hack to make `python setup.py sdist` work in a vagrant vbox vm
if os.environ.get('USER','') == 'vagrant':
    del os.link

def read(filen):
    with open(os.path.join(os.path.dirname(__file__), filen), "r") as fp:
        return fp.read()
 
setup (
    name = "bubbler",
    version = "0.1",
    description="Python Events",
    long_description=read("README.md"),
    author="Alec Elton",
    author_email="alec.elton@gmail.com", # Removed to limit spam harvesting.
    url="https://github.com/basementcat/bubbler",
    packages=["bubbler", "tests"],
    test_suite="nose.collector",
    install_requires=[],
    setup_requires=['nose>=1.0'],
    tests_require=["nose"]
)