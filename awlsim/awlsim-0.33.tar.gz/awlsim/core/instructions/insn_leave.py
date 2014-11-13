# -*- coding: utf-8 -*-
#
# AWL simulator - instructions
#
# Copyright 2012-2014 Michael Buesch <m@bues.ch>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from __future__ import division, absolute_import, print_function, unicode_literals
from awlsim.common.compat import *

from awlsim.core.instructions.main import * #@nocy
from awlsim.core.operators import *
#from awlsim.core.instructions.main cimport * #@cy


class AwlInsn_LEAVE(AwlInsn): #+cdef
	def __init__(self, cpu, rawInsn):
		AwlInsn.__init__(self, cpu, AwlInsn.TYPE_LEAVE, rawInsn)
		self.assertOpCount(0)

	def run(self):
#@cy		cdef S7StatusWord s

		if not self.cpu.is4accu:
			raise AwlSimError("LEAVE not supported on 2-accu CPU")
		self.cpu.accu2.setDWord(self.cpu.accu3.getDWord())
		self.cpu.accu3.setDWord(self.cpu.accu4.getDWord())
