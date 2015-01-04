def print_list(the_list,level):
		for each_item in the_list:
				if isinstance(each_item,list):
						print_list(each_item,level+1)
				else:
					for tab_stop in range(level):
						print"\t",
					print(each_item)