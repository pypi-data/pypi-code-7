#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup, find_packages

import os
import re


setup(name='yieldfrom.urllib3',

      version='0.1.2',

      description="Asyncio HTTP library with thread-safe connection pooling, file post, and more.",
      long_description=open('README.rst').read() + '\n\n' + open('CHANGES.rst').read(),
      classifiers=[
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Software Development :: Libraries',
      ],
      keywords='urllib httplib asyncio filepost http https ssl pooling',

      author='Andrey Petrov',
      author_email='andrey.petrov@shazow.net',
      maintainer='David Keeney',
      maintainer_email='dkeeney@rdbhost.com',

      url='http://urllib3.readthedocs.org/',
      license='MIT',

      packages=['yieldfrom', 'yieldfrom.urllib3',
                'yieldfrom.urllib3.packages', 'yieldfrom.urllib3.packages.ssl_match_hostname',
                'yieldfrom.urllib3.util',
                ],
      #packages=find_packages(exclude=['test\*', 'test', 'dummyserver', 'dummyserver\*', '__pycache__']),
      #packages=find_packages('yieldfrom'),
      package_dir={'yieldfrom': 'yieldfrom'},
      install_requires=['yieldfrom.http.client', 'setuptools'],
      namespace_packages=['yieldfrom'],
      zip_safe=False,
      )
