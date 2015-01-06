#!/usr/bin/env python2.6

import os
import setuptools


setuptools.setup(
  name='clicast',
  version='0.4.5',

  author='Max Zheng',
  author_email='maxzheng.os @t gmail.com',

  description=open('README.rst').read(),

  entry_points={
    'console_scripts': [
      'cast = clicast.editor:cast',
    ],
  },

  install_requires=[
    'remoteconfig',
    'requests',
  ],

  license='MIT',

  package_dir={'': 'src'},
  packages=setuptools.find_packages('src'),
  include_package_data=True,

  setup_requires=['setuptools-git'],

#  scripts=['bin/cast-example'],

  classifiers=[
    'Development Status :: 5 - Production/Stable',

    'Intended Audience :: Developers',
    'Topic :: Software Development :: Development Tools',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
  ],

  keywords='cli broadcast command warning critical bug',
)
