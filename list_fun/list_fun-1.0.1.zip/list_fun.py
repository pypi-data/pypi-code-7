Python 3.4.2 (v3.4.2:ab2c023a9432, Oct  6 2014, 22:16:31) [MSC v.1600 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
"""这是list_fun模块，提供了一个list_fun（）函数，这个函数的作用是打印列表，其中有可能包含（也可能不包含）嵌套列表"""
>>> def list_fun(the_list,level):
"""入参the_list，指要打印的列表名称"""
	for round_list in the_list:
		if isinstance(round_list,list):
			list_fun(round_list,level+1)
		else:
			for num in range(level):
				print("\t",end='')
			print(round_list)
