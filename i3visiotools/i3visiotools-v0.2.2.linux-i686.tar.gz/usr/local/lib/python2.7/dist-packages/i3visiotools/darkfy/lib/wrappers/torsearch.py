# -*- coding: cp1252 -*-
#
##################################################################################
#
#	This file is part of darkfy.py.
#
#	Darkfy is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##################################################################################


from darkengine import DarkEngine

class Torsearch(DarkEngine):
	''' 
		<Torsearch> class.
	'''
	def __init__(self):
		''' 
			Constructor without parameters.
			Most of the times, this will be the ONLY method needed to be overwritten.
		'''
		# This is the tag of the DarkEngine
		self.name = "i3visio.torsearch"
		# This is the string containing the regexp to be seeked
		self.url = "https://torsearch.es/en/search?q=" + "<THE_WORD>"
		
		self.delimiters = {}
		self.delimiters["start"] = "<div class='page-listing col-sm-12'>"
		self.delimiters["end"] = "<div class='row'>"
		
		self.fields = {}
		self.fields["i3visio.text"] = {"start": "<div class='description'>", "end": "</div>"}
		self.fields["i3visio.title"] = {"start": "<div class='title'>", "end": "</a>"}
		self.fields["i3visio.url"] = {"start": "<span class='path'>", "end": "</span>"}
