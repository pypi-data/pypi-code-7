# -*- coding: utf-8 -*-

#--------------------------------------------------------------------
# Copyright (c) 2015 Eren Inan Canpolat
# Author: Eren Inan Canpolat <eren.canpolat@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------

from setuptools import setup
import re

version = "0.1.2"
description = "Nota Bene: Keep track of your notes."
url = "https://github.com/canpolat/nb"
author = "Eren Inan Canpolat"
author_email = "eren.canpolat@gmail.com"

setup(name='nb',
	version=version,
	description=description,
	long_description=open('README.rst').read(),
	classifiers=[
                'Development Status :: 2 - Pre-Alpha',
		'Environment :: Console',
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Natural Language :: English',
		'Programming Language :: Python :: 2.7',
	],
	url=url,
	author=author,
	author_email=author_email,
	packages=['nb'],
	entry_points={
		'console_scripts': [
			'nb = nb:main',
		],
	},
	install_requires=[
		"docopt>=0.6.2",
                "PyYAML>=3.11",
	],
	include_package_data=True,
	zip_safe=False)
