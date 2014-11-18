#!/usr/bin/env python
# coding: utf-8
"""
   File Name: setup.py
      Author: Wan Ji
      E-mail: wanji@live.com
  Created on: Tue 18 Mar 2014 12:03:18 PM CST
 Description:
"""

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print "warning: pypandoc module not found, DONOT convert Markdown to RST"
    read_md = lambda f: open(f, 'r').read()


def runcmd(cmd):
    """ Run command.
    """
    os.system(cmd)


setup(name='irbench',
      version='0.0.67',
      author='WAN Ji',
      author_email='wanji@live.com',
      package_dir={'irbench': 'src'},
      packages=['irbench'],
      scripts=['bin/bench.py',
               'bin/dsinit.py',
               'tools/bow2sparsedir.py',
               'tools/bow2sparse.py'],
      url='https://github.com/wanji/irbench',
      # license='LICENSE.txt',
      description='Image Retrieval Benchmark.',

      long_description=read_md("DESC.md"),
      install_requires=[
          "numpy      >= 1.6.0",
          "scipy      >= 0.9.0",
          "bottleneck >= 0.8.0",
          "bitmap     >= 0.0.1",
          "protobuf   >= 2.4.0",
      ],
      )
