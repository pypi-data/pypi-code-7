#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of jottacloudclient.
#
# jottacloudclient is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jottacloudclient is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with jottacloudclient.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014 Håvard Gulldahl <havard@gulldahl.no>

from setuptools import setup

import os, sys
sys.path.insert(0, './src')

from jottacloudclient import __version__

try:
    os.system('pandoc --from=markdown --to=rst --output=README.txt README.md')
    with open('README.txt') as f:
        long_desc = f.read()
except:
    long_desc = ''

package_version = '1'

setup(name='jottacloudclient',
      version='%s-%s' % (__version__, package_version),
      license='GPLv3',
      description='A cli friendly sync client for JottaCloud',
      long_description=long_desc,
      author=u'Håvard Gulldahl',
      author_email='havard@gulldahl.no',
      url='https://gitorious.org/jottafs/jottacloudclient.git',
      package_dir={'':'src'},
      packages=['jottacloudclient', ],
      scripts=['src/jottacloudclientmonitor.py', 'src/jottacloudclientscanner.py'],
      install_requires=['jottalib>=0.2.10',
                        'clint',
                        ],
     )


