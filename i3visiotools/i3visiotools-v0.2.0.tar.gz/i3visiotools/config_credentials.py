# -*- coding: cp1252 -*-
#
##################################################################################
#
#	This file is part of i3visiotools.
#
#	i3visiotools is free software: you can redistribute it and/or modify
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

def returnListOfCreds():
	'''
		:return: A list of tuples containing in the first the name of the platform
	'''
	listCreds = []
	#listCreds.append(("<platform>", "<username>", "<password>"))
	#
	# The platforms that need a username and password are the following. 
	# Uncomment the lines and change the <user> and <pass>.
	#
	listCreds.append(("tripit", "ursula.visio@gmail.com", "MolamoS87"))
	listCreds.append(("wordreference", "ursula-visio", "iqVZYFTIRTVueE08zEVY"))
	listCreds.append(("rapid", "ursula.visio", "slOkYPqjrV6texLSjBMB"))
	listCreds.append(("eqe", "ursulavisio", "Ur5cNOkWwG9v5wF61r7v"))
	return listCreds
