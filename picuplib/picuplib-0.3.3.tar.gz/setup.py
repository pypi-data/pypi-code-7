#!/usr/bin/env python
# -*- coding:utf8 -*-

from setuptools import setup

import picuplib


setup(
      name = 'picuplib',
      packages = ['picuplib'],
      version = picuplib.__version__,
      description = 'Picflash upload library',
      author = 'Arvedui',
      author_email = 'arvedui@posteo.de',
      url = 'https://github.com/Arvedui/picuplib',
      install_requires=['requests', 'requests-toolbelt'],
      classifiers=[
            'Development Status :: 4 - Beta',
            'Topic :: Software Development :: Libraries',
            'Intended Audience :: Developers',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            ]
      )
