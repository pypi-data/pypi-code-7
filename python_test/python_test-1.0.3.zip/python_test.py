"""这个模块实现了打印一个列表的功能，能将嵌套在列表中的列表内容也逐一打印出来，次级列表会缩进打印"""
def print_lol(the_list,level=0):
	"""the_list 为目标打印列表，indent参数让用户选择是否需要缩进缺省值为False不需要，level为列表嵌套的层数，0为缺省参数以防用户忘记输入level或是之前引用后引起缺少参数报错的问题"""
	for each_item in the_list:
		if isinstance (each_item,indent=False,list):
			"""isinstance 判断目标是否为list类型是的话直接打印内容，否的话识别出是嵌套列表，level增加1后在else后打印制表符就会增加一个空格表示为下一层"""
			print_lol(each_item,level+1)
		else:
                        if indent:
                                """若需要缩进则根据level值缩进"""
                                for print_stop in range(level):
                                        """根据level值打印该值数量的空格，在空格后打印列表中的内容"""
                                        print("\t",end='')
			print(each_item)
