#! /usr/bin/env python
# -*- coding=utf-8 -*-

from distutils.core import setup
setup(
    name='pythis',
    version='1.4',

    description='zen of python in Simplified Chinese',
    url='https://github.com/vincentping/pythis',
    author='Vincent Ping',
    author_email='vincentping@gmail.com',
    license='MIT',
    classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 4 - Beta',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
],
    py_modules=['pythis'],
    keywords='zen python chinese',
    )
#EOF