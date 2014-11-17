#! /usr/bin/env python

import os
import sys

from setuptools import setup

import django_py3s3


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as file:
    README = file.read()

with open(os.path.join(os.path.dirname(__file__), 'LICENSE')) as file:
    LICENSE = file.read()


CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Natural Language :: English',
    'Framework :: Django',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Internet',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Utilities',
]


setup(name='django_py3s3',
      version=django_py3s3.__version__,
      author=django_py3s3.__author__,
      author_email=django_py3s3.__email__,
      maintainer=django_py3s3.__author__,
      maintainer_email=django_py3s3.__email__,
      url='http://github.com/logston/django_py3s3',
      description='A Django storage backend for saving files to AWS S3.',
      long_description=README,
      license=LICENSE,
      classifiers=CLASSIFIERS,
      packages=['django_py3s3'],
      include_package_data=True,
      package_data={'': ['LICENSE', 'README.rst']})
