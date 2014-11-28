# -*- coding: utf-8 -*-
'''
Created on Oct 22, 2013

@author: Arturo Curiel
'''

from distutils.core import setup
from setuptools import find_packages

with open('README.txt') as f:
    long_description = f.read()

setup(name='nixtla',
      version='5.3.7',
      author=u'Arturo Curiel',
      author_email=u'curiel@irit.fr',
      description='Formulae-based annotation for Sign Language corpora',
      long_description=long_description,
      packages=find_packages(),
      include_package_data=True,
      license='CeCILL Version 2.1',
      install_requires = [
          'pyparsing<=2.0.2',
          'numpy<=1.9.0',
          'zope.component<=4.2.0',
          'zope.interface<=4.1.1',
          'ply<=3.4',
          'python-magic<=0.4.6',
          'pandas<=0.15.1',
          # 'cv',
      ],
      url='http://www.irit.fr/-TCI-team-?lang=en',
      zip_safe=False,
      classifiers=[
                'Intended Audience :: Science/Research',
                'Topic :: Scientific/Engineering :: Human Machine Interfaces',
                'Topic :: Scientific/Engineering :: Information Analysis',
                ],
)
