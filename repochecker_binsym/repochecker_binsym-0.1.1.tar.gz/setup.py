#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup

setup(name = 'repochecker_binsym',
      version = '0.1.1',
      description = 'Repository checker that validates completeness of a linux repository over binary symbols',
      author = 'Rosa labs & HSE',
      packages = ['repochecker_binsym'],
      install_requires = [ 'PyYAML', 'python-libarchive', 'pyelftools' ],
      classifiers = [
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities',
      ],
      url = 'https://abf.io/gluk47/repochecker_binsym',
      test_suite = 'nose.collector',
      tests_require = ['nose'],
      zip_safe = False)
