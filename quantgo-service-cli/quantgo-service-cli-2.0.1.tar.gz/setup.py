#!/usr/bin/env python

"""
distutils/setuptools install script.
"""

import service_cli

try:
    from setuptools import setup
    setup
except ImportError:
    from distutils.core import setup


packages = ['service_cli', ]

requires = ['argparse>=1.1',
            ]


setup(
    name='quantgo-service-cli',
    version=service_cli.__version__,
    description='QuantGo User Service Command Line Tool.',
    long_description=open('README.md').read(),
    author='Nikolay Krysiuk',
    author_email='nikolay@quantgo.com',
    url='https://quantgo.com',
    scripts=['bin/service', 'bin/service_complete'],
    packages=packages,
    package_dir={'service_cli': 'service_cli'},
    install_requires=requires,
    license=open("LICENSE.txt").read(),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Intended Audience :: End Users/Desktop',
    ),
    keywords=['quantgo', 'quantgo-service', 'quantgo-service-cli']
)
