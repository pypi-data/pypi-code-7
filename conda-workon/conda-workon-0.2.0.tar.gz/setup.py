#!/usr/bin/env python

from __future__ import absolute_import, print_function, division

from setuptools import setup


setup(
    name='conda-workon',
    description='Activate conda environments in subshells',
    long_description=open('README.rst').read(),
    version='0.2.0',
    author='Floris Bruynooghe',
    author_email="flub@devork.be",
    url='https://bitbucket.org/flub/conda-workon',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Environment :: Console',
    ],
    py_modules=['conda_workon'],
    entry_points={'console_scripts': ['conda-workon = conda_workon:main']},
    install_requires=['conda'],
)
