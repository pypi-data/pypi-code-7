def splitList(listParam) :
	for eachElement in listParam :
		if isinstance(eachElement, list) :
			splitList(eachElement)
		else :
			print(eachElement)