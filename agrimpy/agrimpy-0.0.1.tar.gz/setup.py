#!/usr/bin/python
# -*- coding: UTF-8 -*-

from distutils.core import setup

setup(
    name='agrimpy',
    version='0.0.1',
    author='Santiago Pestarini',
    author_email='santiago@pestarini.com.ar',
    packages=['agrimpy'],
    package_data={'agrimpy': ['coord/*']},
    url='http://pypi.python.org/pypi/agrimpy/',
    license='LICENSE.txt',
    description='Algunas operaciones con coordenadas geodésicas.',
    long_description=open('README.rst').read(),
)
