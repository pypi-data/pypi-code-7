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


import os
import re
import copy
# logging imports
import logging
import i3visiotools.browser as usufybrowser

class DarkEngine():
	''' 
		<DarkEngine> class.
	'''
	def __init__(self):
		''' 
			Constructor without parameters...
			Most of the times, this will be the ONLY method needed to be overwritten.
		'''
		# This is the tag of the regexp
		self.name = "<empty>"
		# This is the string containing the regexp to be seeked
		self.url = "http://example.com/?q=" + "<THE_WORD>"
		
		self.delimiters = {}
		self.delimiters["start"] = "<start_text>"
		self.delimiters["end"] = "<end_text>"
	
		self.fields = {}
	
	def __str__(self):
		''' 
			Function to obtain the text that represents this object.
			
			:return:	str(self.getJson())
		'''
		return str(self.name)
		
	def getResults(self, word = None):
		''' 
			Function to recover the.
			
			:param word:	word to be searched.

			:return:	The output format will be like:
				{"email" : {"reg_exp" : "[a-zA-Z0-9\.\-]+@[a-zA-Z0-9\.\-]+\.[a-zA-Z]+" , "found_exp" : ["foo@bar.com", "bar@foo.com"] } }
		'''
		logger = logging.getLogger("darkfy")
		searchURL = self.url.replace("<THE_WORD>", word)
		
		logger.debug("Recovering the targetted url (authenticated)...")
		uBrowser = usufybrowser.UsufyBrowser()
		html = uBrowser.recoverURL(searchURL)	

		start = self.delimiters["start"]
		end = self.delimiters["end"]
		
		values = re.findall(start + "(.*?)" + end, html, re.DOTALL)
		

		parsedResults = []
		for val in values:
			newResource = {}
			for field in self.fields.keys():
				# Performing teh regular expression to extract the resources
				foundElems = re.findall(self.fields[field]["start"] + "(.*?)" + self.fields[field]["end"], val, re.DOTALL)
				# We clean all the elements found
				newResource[field] = self.cleanSpecialChars(foundElems)
			parsedResults.append(newResource)
		return parsedResults

	def cleanSpecialChars(self, auxList):
		'''
			Method that cleans any text deleting certain special characters and avoiding the text between '<' and '>'.
	
			:param auxList:	Any list of strings.
			:return:	A cleaned list of strings.
		'''

		final = []
		cleaningChars = ["\n", "\t", "\r"]
		for elem in auxList:				
			for c in cleaningChars:
				elem = elem.replace(c, '')
			# Deleting html tags from in between and putting an space instead
			elem = re.sub(r'<.+?>', ' ', elem)
			final.append(elem)
		return final
