#!/usr/bin/env python

from distutils.core import setup

setup(name='petlib',
      version='0.0.1',
      description='A library implementing a number of Privacy Enhancing Technologies (PETs)',
      author='George Danezis',
      author_email='g.danezis@ucl.ac.uk',
      url=r'http://www.cs.ucl.ac.uk/students/syllabus/mscisec/ga17_privacy_enhancing_technologies/',
      packages=['petlib'],
      license="LICENSE.txt",
      long_description=open("README").read(),
      install_requires=[
      			"cffi >= 0.8.2"
      ],
     )