#!/usr/bin/env python

# ======================= QuantGo Copyright Notice ============================
# Copyright 2013 QuantGo, LLC.  All rights reserved.
# Permission to use solely inside a QuantGo Virtual Quant Lab
# Written By: Nikolay
# Date: 12-12.2013
# ======================= QuantGo Copyright Notice ============================

"""
distutils/setuptools install script.
"""

import qg_cli

try:
    from setuptools import setup
    setup
except ImportError:
    from distutils.core import setup


packages = ['qg_cli', ]

requires = ['argparse>=1.1',
            'validictory>=0.8.3',
            'requests==1.2.3',
           ]


setup(
    name='quantgo-cli',
    version=qg_cli.__version__,
    description='QuantGo Command Line Tool.',
    long_description=open('doc/README.md').read(),
    author='Nikolay Krysiuk',
    author_email='nikolay@quantgo.com',
    url='https://quantgo.com',
    scripts=['bin/quantgo', 'bin/quantgo_complete'],
    packages=packages,
    package_dir={'qg_cli': 'qg_cli'},
    install_requires=requires,
    license=open("LICENSE.txt").read(),
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Intended Audience :: End Users/Desktop',
    ),
    keywords=['quantgo', 'quantgo-cli', 'quantgo-user-cli']
)
