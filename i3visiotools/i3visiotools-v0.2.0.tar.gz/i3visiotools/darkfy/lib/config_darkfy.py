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
import copy
import i3visiotools.logger as logger
import logging
# Importing Classes of <RegexpObject> objects that will be used in the script. The files are stored in the regexp folder.
# For demo only
#from regexp.demo import Demo
from wrappers.torsearch import Torsearch
from wrappers.ahmia import Ahmia
# Add any additional import here
#from regexp.anynewregexp import AnyNewRegexp
# <ADD_NEW_REGEXP_IMPORT_BELOW>
# Please, notify the authors if you have written a new regexp.

def getAllDarkEngines():
	''' 
		Method that recovers ALL the list of <DarkEngine> classes to be processed....

		:return:	Returns a list [] of <DarkEngine> classes.
	'''
	logger = logging.getLogger("darkfy")

	logger.debug("Recovering all the available <DarkEngine> classes.")
	listAll = []
	# For demo only
	#listAll.append(Demo())
	listAll.append(Torsearch())
	listAll.append(Ahmia())
	# Add any additional import here
	#listAll.append(AnyNewRegexp)
	# <ADD_NEW_REGEXP_TO_THE_LIST>
	# Please, notify the authors if you have written a new regexp.

	logger.debug("Returning a list of " + str(len(listAll)) + " <DarkEngine> classes.")
	return listAll
