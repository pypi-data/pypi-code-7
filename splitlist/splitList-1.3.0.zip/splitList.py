def splitList(listParam, indent=False, level=0) :
	for eachElement in listParam :
		if isinstance(eachElement, list) :
			splitList(eachElement, indent, level+1)
		else :
			if indent :
				for tab_stop in range(level) :
					print("\t", end='')
			print(eachElement)

