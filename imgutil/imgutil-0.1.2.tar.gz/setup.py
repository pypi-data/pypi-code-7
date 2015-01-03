#!/usr/bin/env python

from os.path import exists
from setuptools import setup, find_packages

setup(
    name='imgutil',
    version='0.1.2',
    # Your name & email here
    author='yuliang',
    author_email='yu.liang@thekono.com',
    # If you had imgutil.tests, you would also include that in this list
    packages=find_packages(),
    # Any executable scripts, typically in 'bin'. E.g 'bin/do-something.py'
    scripts=[],
    # REQUIRED: Your project's URL
    url='',
    # Put your license here. See LICENSE.txt for more information
    license='',
    # Put a nice one-liner description here
    description='Image operation utilities.',
    long_description=open('README.md').read() if exists("README.md") else "",
    # Any requirements here, e.g. "Django >= 1.1.1"
    install_requires=[
        'Pillow >= 2.7.0',
    ],
)
