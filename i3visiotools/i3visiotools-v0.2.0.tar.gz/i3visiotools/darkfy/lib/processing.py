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
import time

# configuration and utils
import i3visiotools.darkfy.lib.config_darkfy as config
import i3visiotools.general as general

# logging imports
import i3visiotools.logger
import logging


def searchTerms(words = [], output = None):
	''' 
		Method that looks for the words in the Deep Web.

		:param words:	List of words to be searched.
		:param output:	File where the results will be stored.

		:return:	A dict containing the results.
	'''
	logger = logging.getLogger("darkfy")
	#TO-DO: let the user select which platforms he want to search		
	platforms = config.getAllDarkEngines()
	
	allResults = {}
	
	for word in words:
		allResults[word] = {}
		for plat in platforms:
			# Defining the list of results
			allResults[word][str(plat)] = []
			allResults[word][str(plat)] = plat.getResults(word)
				
	#strTime = general.getCurrentStrDatetime()			
	#strTime = lib.general.getCurrentStrDatetime()
	logger.info("Writing results to json file")
	jsonData = general.dictToJson(allResults)
	if output != None:
		with open (os.path.join(output), "w") as oF:
			oF.write( jsonData + "\n")				
	
	logger.info(jsonData)

	return allResults


def darkfy_main(args):
	''' 
		Main function. This function is created in this way so as to let other applications make use of the full configuration capabilities of the application.	
	'''
	# Recovering the logger
	logger = darkfy.lib.logger.setupDarkfyLogger(args.verbose)
	# From now on, the logger can be recovered like this:
	logger = logging.getLogger("darkfy")

	logger.info("""darkfy.py Copyright (C) F. Brezo and Y. Rubio (i3visio) 2014
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain conditions.
For details, run:
\tpython darkfy.py --license""")
	
	logger.info("Starting darkfy.py...")

	if args.license:
		logger.info("Looking for the license...")
		# showing the license
		try:
			with open ("COPYING", "r") as iF:
				contenido = iF.read().splitlines()
				for linea in contenido:	
					print linea
				return contenido
		except Exception:
			logger.error("ERROR: there has been an error when opening the COPYING file.\n\tThe file contains the terms of the GPLv3 under which this software is distributed.\n\tIn case of doubts, verify the integrity of the files or contact contacto@i3visio.com.")
	else:
		# Defining the list of words to monitor to monitor
		words = []
		logger.debug("Recovering nicknames to be processed...")
		if args.words:
			words = args.words
		else:
			# Reading the nick files
			try:
				words = args.list.read().splitlines()
			except:
				logger.error("ERROR: there has been an error when opening the file that stores the nicks.\tPlease, check the existence of this file.")
		return searchTerms(words=words, output=args.output)

