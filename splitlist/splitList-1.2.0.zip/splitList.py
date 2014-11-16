def splitList(listParam, level=0) :
	for eachElement in listParam :
		if isinstance(eachElement, list) :
			splitList(eachElement, level+1)
		else :
			for tab_stop in range(level) :
				print("\t", end='')
			print(eachElement)

