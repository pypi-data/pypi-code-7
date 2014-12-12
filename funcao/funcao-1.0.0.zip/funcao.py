def procurarlist(array):
	for each_item in array:
		if(isinstance(each_item, list)):
			procurarlist(each_item)
		else:
			print(each_item)


array = ["Oi", ["Ta na hora de jantar", "Não sei mais o que escrever"], "Tchau"]
procurarlist(array)
