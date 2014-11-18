'''
Created on 17 Nov 2014

@author: swest
'''

#from distutils.core import setup
from setuptools import setup

files = ['input/*', 'out/*']

setup(
      name = 'listoliver',
      version = '1',
      description = 'description',
      author = 'Oliver Bonham-Carter and Sean West',
      url = 'tbd',
      packages = ['lister'],
      package_data = {'package' : files},
      entry_points = {
                      'console_scripts':[
                                         'lister = lister.lister:smain'
                                         ]
                      },
      scripts = ['run_lister'],
      long_description = 'long description',
      classifiers = ['Programming Language :: Python', \
                     'Programming Language :: Python :: 3', \
                     'Operating System :: Unix', \
                     'Development Status :: 1 - Planning', \
                     'Intended Audience :: Science/Research', \
                     'Topic :: Scientific/Engineering :: Bio-Informatics', \
                     'Topic :: Scientific/Engineering :: Mathematics', \
                     'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', \
                     'Natural Language :: English']
      )
