#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup


with open('README.rst') as f:
    long_description = f.read()

setup(name='war2maff',
      version="0.0.1",
      author="Matěj Cepl",
      author_email="mcepl@cepl.eu",
      url="https://gitlab.com/mcepl/war2maff",
      description=("Web archives conversion from WAR (by Konqueror) " +
                   "to Mozilla’s MAFF"),
      long_description=long_description,
      license="GPLv3",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 2',
          'Topic :: Internet :: WWW/HTTP :: Browsers',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
      ],
      install_requires=['lxml'],
      test_suite="test",
      include_package_data=True,
      zip_safe=True
      )
