#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptricks import Package, md_readme_as_rst


INSTALL_REQUIRES = (
    []
)

s = Package('setuptricks')
s.before_setup()
setup(
    name=s.package,
    version=s.version,
    description=s.description,
    long_description=md_readme_as_rst(),
    license='MIT License',
    author='Andy Hayden',
    author_email='andyhayden1@gmail.com',
    url='https://github.com/hayd/setuptricks',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='setup',
    install_requires=INSTALL_REQUIRES,
    packages=s.packages,
    test_suite='tests',
)
