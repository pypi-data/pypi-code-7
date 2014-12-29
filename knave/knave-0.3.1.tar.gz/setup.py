#!/usr/bin/env python

# Copyright 2014 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
from setuptools import setup, find_packages

VERSIONFILE = "knave/__init__.py"


def get_version():
    with open(VERSIONFILE, 'rb') as f:
        return re.search("^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                           f.read().decode('UTF-8'), re.M).group(1)


def read(*path):
    """
    Return content from ``path`` as a string
    """
    with open(os.path.join(os.path.dirname(__file__), *path), 'rb') as f:
        return f.read().decode('UTF-8')

setup(
    name='knave',
    version=get_version(),
    description='Authorization library for WSGI applications',
    long_description=read('README.rst') + "\n\n" + read("CHANGELOG.rst"),
    url='https://bitbucket.org/ollyc/knave',
    author='Oliver Cope',
    author_email='oliver@redgecko.org',
    keywords=['authorization', 'authorisation', 'authentication', 'security',
              'wsgi'],
    license='Apache',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=[],
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',
)
