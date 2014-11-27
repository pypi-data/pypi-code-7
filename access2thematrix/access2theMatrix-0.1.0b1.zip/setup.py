# -*- coding: utf-8 -*-
from setuptools import setup
import sys

if len(sys.argv) == 1:
    sys.argv.append('sdist')

setup(name = 'access2theMatrix',
      version = '0.1.0b1',
      description = 'Omicron NanoTechnology\'s MATRIX Control System result'
      ' file accessing tool',
      long_description = 'access2theMatrix is a tool for accessing Omicron'
      ' NanoTechnology\'s MATRIX Control System result files. Only topography'
      ' image data will be accessed by this tool.',
      url = '',
      author = 'Stephan Zevenhuizen',
      author_email = 'S.J.M.Zevenhuizen@uu.nl',
      license = 'GPLv3+',
      keywords = 'SPM scanning probe microscopy image analysis',
      classifiers = ['Development Status :: 4 - Beta',
                     'Intended Audience :: Science/Research',
                     'License :: OSI Approved :: GNU General Public License v3'
                     ' or later (GPLv3+)',
                     'Natural Language :: English',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python :: 2.7',
                     'Topic :: Scientific/Engineering :: Chemistry',
                     'Topic :: Scientific/Engineering :: Information Analysis',
                     'Topic :: Scientific/Engineering :: Physics',
                     'Topic :: Software Development :: Libraries ::'
                     ' Python Modules'],
      packages = ['access2thematrix'],
      package_data = {'access2thematrix': ['LICENSE.txt']})
