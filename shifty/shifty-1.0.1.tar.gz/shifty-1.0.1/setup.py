#!/usr/bin/env python
#    -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

#    Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

import shifty

setup(
    name="shifty",
    packages=find_packages(exclude=('tests',)),
    version=shifty.__version__,
    url=shifty.__url__,
    author=shifty.__author__,
    author_email=shifty.__email__,
    description=shifty.__short_description__,
    license="GNU General Public License",
    platforms=['any'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe=False,
    keywords='algorithms',
    install_requires=['nose>=1.3.1',
                      'coverage>=3.7.1'],
)
