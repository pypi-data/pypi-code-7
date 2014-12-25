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

class Ahmia(DarkEngine):
	''' 
		<Ahmia> class.
	'''
	def __init__(self):
		''' 
			Constructor without parameters.
			Most of the times, this will be the ONLY method needed to be overwritten.
		'''
		# This is the tag of the DarkEngine
		self.name = "i3visio.ahmia"
		# This is the string containing the regexp to be seeked
		self.url = "https://ahmia.fi/search/?q=" + "<THE_WORD>"
		
		self.delimiters = {}
		self.delimiters["start"] = "<li class=\"hs_site\">"
		self.delimiters["end"] = "</li>"
		
		self.fields = {}
		self.fields["i3visio.date"] = {"start": "<p class=\"urlinfo\">", "end": "</p>"}
		self.fields["i3visio.text"] = {"start": "<div class=\"urltext\">", "end": "</div>"}
		self.fields["i3visio.title"] = {"start": "<h3>", "end": "</h3>"}
		self.fields["i3visio.url"] = {"start": "<p class=\"links\">Access without Tor Browser: ", "end": "</a>"}

		
