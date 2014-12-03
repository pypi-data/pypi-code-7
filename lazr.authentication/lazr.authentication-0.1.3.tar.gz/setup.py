#!/usr/bin/env python

# Copyright 2009 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.authentication
#
# lazr.authentication is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.authentication is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.authentication.  If not, see <http://www.gnu.org/licenses/>.

import sys
from setuptools import setup, find_packages

# generic helpers primarily for the long_description
def generate(*docname_or_string):
    res = []
    for value in docname_or_string:
        if value.endswith('.txt'):
            f = open(value)
            value = f.read()
            f.close()
        res.append(value)
        if not value.endswith('\n'):
            res.append('')
    return '\n'.join(res)
# end generic helpers


__version__ = open("src/lazr/authentication/version.txt").read().strip()

setup(
    name='lazr.authentication',
    version=__version__,
    namespace_packages=['lazr'],
    packages=find_packages('src'),
    package_dir={'':'src'},
    include_package_data=True,
    zip_safe=False,
    maintainer='LAZR Developers',
    maintainer_email='lazr-developers@lists.launchpad.net',
    description=open('README.txt').readline().strip(),
    long_description=generate(
        'src/lazr/authentication/README.txt',
        'src/lazr/authentication/NEWS.txt'),
    license='LGPL v3',
    install_requires=[
        'httplib2',
        'oauth',
        'setuptools',
        'wsgi_intercept',
        'zope.interface',
        ],
    url='https://launchpad.net/lazr.authentication',
    download_url= 'https://launchpad.net/lazr.authentication/+download',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python"],
    extras_require=dict(
        docs=['Sphinx',
              'z3c.recipe.sphinxdoc']
    ),
    # This does not play nicely with buildout because it downloads but does
    # not cache the package.
    #setup_requires=['eggtestinfo', 'setuptools_bzr'],
    test_suite='lazr.authentication.tests',
    )
