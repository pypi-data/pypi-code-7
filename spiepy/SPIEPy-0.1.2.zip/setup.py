# -*- coding: utf-8 -*-
from setuptools import setup
from codecs import open
from os import path
import sys

if len(sys.argv) == 1:
    sys.argv.append('sdist')

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.txt'), encoding = 'utf-8') as f:
    long_description = f.read().replace('\r\n', '\n').expandtabs(4)

setup(name = 'SPIEPy',
      version = __import__('spiepy').__version__,
      description = 'SPIEPy (Scanning Probe Image Enchanter using Python) is a'
      ' Python library to improve automatic processing of SPM images.',
      long_description = long_description,
      url = '',
      author = 'Stephan Zevenhuizen',
      author_email = 'S.J.M.Zevenhuizen@uu.nl',
      license = 'The license file is in the package.',
      keywords = 'SPM scanning probe microscopy image analysis flattening nano'
      ' nanotechnology',
      classifiers = ['Development Status :: 5 - Production/Stable',
                     'Intended Audience :: Science/Research',
                     'License :: OSI Approved :: BSD License',
                     'Natural Language :: English',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python :: 2.7',
                     'Topic :: Scientific/Engineering :: Chemistry',
                     'Topic :: Scientific/Engineering :: Information Analysis',
                     'Topic :: Scientific/Engineering :: Physics',
                     'Topic :: Software Development :: Libraries ::'
                     ' Python Modules'],
      packages = ['spiepy', 'spiepy.demo'],
      package_data = {'spiepy': ['LICENSE.txt'],
                      'spiepy.demo': ['image_with_defects.dat',
                                      'image_with_step_edge.dat',
                                      'image_with_step_edge_and_atoms.dat']})
