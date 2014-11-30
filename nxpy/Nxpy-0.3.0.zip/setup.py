# nxpy package ---------------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Packaging information.

"""

from __future__ import absolute_import

import codecs
import os.path

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here,'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name = 'Nxpy',
    version = '0.3.0',
    url = 'http://nxpy.sourceforge.net',
    author = 'Nicola Musatti',
    author_email = 'nmusatti@users.sf.net',
    packages = find_packages(exclude=["*._test", "*._test.*", "_test.*", "_test"]),
    #package_data = { '' : [ '*.txt', '*.rst', ], },
    install_requires = ['six >= 1.8.0'],
    license = 'Boost Software License version 1.0',
    description = "Nick's Python Toolchest",
    long_description = long_description,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',

    ],
)
