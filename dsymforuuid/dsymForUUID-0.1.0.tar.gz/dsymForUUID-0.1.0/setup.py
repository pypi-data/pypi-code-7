# -*- coding: utf-8 -*-
from setuptools import setup

with open('README.rst', 'r') as f:
    long_desc = f.read().decode('utf-8')

setup(name='dsymForUUID',
      version='0.1.0',
      description='Locate dSYM files given their UUID.',
      long_description=long_desc,
      author='Alastair Houghton',
      author_email='alastair@alastairs-place.net',
      url='http://bitbucket.org/al45tair/dsymForUUID',
      license='MIT License',
      scripts=['scripts/dsymForUUID'],
      provides=['dsymForUUID']
)
