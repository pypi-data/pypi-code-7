"""这个模块实现了打印一个列表的功能，能将嵌套在列表中的列表内容也逐一打印出来，次级列表会缩进打印"""
def print_lol(the_list,level):
	"""the_list 为目标打印列表，level为列表嵌套的层数"""
	for each_item in the_list:
		if isinstance (each_item,list):
			"""isinstance 判断目标是否为list类型是的话直接打印内容，否的话识别出是嵌套列表，level增加1后在else后打印制表符就会增加一个空格表示为下一层"""
			print_lol(each_item,level+1)
		else:
			for print_stop in range(level):
				"""根据level值打印该值数量的空格，在空格后打印列表中的内容"""
				print("\t",end='')
			print(each_item)
