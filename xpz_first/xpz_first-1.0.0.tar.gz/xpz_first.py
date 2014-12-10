#coding=utf-8

def xpz_first(the_list):
	for i in the_list:
		if isinstance(i, list):
			xpz_first(i)
		else:
			print i