#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup

setup(name = 'repochecker_binsym',
      version = '0.9.1',
      description = 'Repository checker that validates completeness of a linux repository over binary symbols',
      author = 'Rosa labs & HSE',
      author_email = 'gluk47@gmail.com',
      packages = ['repochecker_binsym'],
      install_requires = [ 'PyYAML', 'python-libarchive', 'pyelftools' ],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities',
      ],
      bugtrack_url = 'https://abf.io/gluk47/repochecker_binsym/issues',
      url = 'https://abf.io/gluk47/repochecker_binsym',
      test_suite = 'nose.collector',
      tests_require = ['nose'],
      zip_safe = False)
