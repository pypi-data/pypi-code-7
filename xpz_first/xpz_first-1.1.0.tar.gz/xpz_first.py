#coding=utf-8


def xpz_first(the_list, level):
	for i in the_list:
		if isinstance(i, list):
			xpz_first(i, level+1)
		else:
			for le in range(level):
				print('\t',end = '')
			print (i)

