#!/usr/bin/python
# -*- coding: UTF-8 -*-

from distutils.core import setup


with open('requirements.txt', 'r') as fh:
    dependencies = [l.strip() for l in fh]


setup(
    name='agrimpy',
    version='0.0.3',
    author='Santiago Pestarini',
    author_email='santiago@pestarini.com.ar',
    packages=['agrimpy'],
    package_data={'agrimpy': ['coord/*']},
    url='http://pypi.python.org/pypi/agrimpy/',
    license='LICENSE.txt',
    description='Algunas operaciones con coordenadas geodésicas.',
    long_description=open('README.rst').read(),
    install_requires=dependencies,
)

