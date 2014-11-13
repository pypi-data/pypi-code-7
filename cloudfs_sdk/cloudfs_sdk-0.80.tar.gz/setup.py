#!/usr/bin/env python

from distutils.core import setup

setup(name='cloudfs_sdk',
      version='0.80',
      description='Python SDK for CloudFS',
      license='MIT',
      author='Bitcasa Inc.',
      author_email='dstrong@bitcasa.com',
      url='https://www.bitcasa.com/cloudfs',
      py_modules=['cloudfs'],
      packages=['cloudfs'],
      install_requires=['requests>=2.4.3'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Topic :: Other/Nonlisted Topic'
      ]
     )