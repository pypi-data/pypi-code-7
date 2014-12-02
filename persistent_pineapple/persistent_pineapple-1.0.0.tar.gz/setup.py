#!/usr/bin/env python
'''package setup script.'''
from __future__ import print_function
import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    print("ERROR: This package requires setuptools in order to install.", file=sys.stderr)
    sys.exit(1)


THIS_DIR = os.path.abspath(os.path.dirname(__file__))
PKG_DIR = os.path.join(THIS_DIR, 'lib')
sys.path.append(PKG_DIR)
# Read the version from our project
from persistent_pineapple import __version__

if __name__ == '__main__':
    setup(
        name="persistent_pineapple",
        version=__version__,
        description="JSON Settings",
        author="Timothy McFadden",
        url="https://github.com/JasonAUnrein/Persistent-Pineapple",
        download_url="https://github.com/JasonAUnrein/Persistent-Pineapple/releases/Persistent-Pineapple-{0}.tar.gz".format(__version__),
        install_requires=[],
        packages=find_packages(),
        package_data={"persistent_pineapple": ['.*']},
        zip_safe=True,
        include_package_data=True,
        test_suite="persistent_pineapple.tests",

        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Other Environment',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Intended Audience :: Developers',
            'Environment :: Console',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Topic :: Software Development :: Libraries'
        ],

        long_description=open(os.path.join(THIS_DIR, "README.rst"), 'r').read()
    )
