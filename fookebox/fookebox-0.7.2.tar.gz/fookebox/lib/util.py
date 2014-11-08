# fookebox, https://github.com/cockroach/fookebox
#
# Copyright (C) 2007-2014 Stefan Ott. All rights reserved.
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

import os

class FileSystem(object):
	@staticmethod
	def exists(path):
		return os.path.exists(path.encode('utf8'))

	@staticmethod
	def isdir(path):
		return os.path.isdir(path.encode('utf8'))

	@staticmethod
	def listdir(path):
		return os.listdir(path.encode('utf8'))
