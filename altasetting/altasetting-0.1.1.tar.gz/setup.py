#!/usr/bin/env python2
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='altasetting',
    version='0.1.1',
    author='Felipe Lerena',
    description='A python settings library',
    author_email='felipelerena@gmail.com',
    packages=['altasetting'],
    scripts=[],
    url='http://github.com/felipelerena/altasetting',
    install_requires=['pyaml',
                      ],
)
