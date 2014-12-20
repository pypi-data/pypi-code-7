# -*- coding: utf-8 -*-


class _CallList(list):

	def __call__(self, *arg, **kwarg):
		return [x(*arg, **kwarg) for x in self]




class ProxyList(list):
	'''TODO'''
	def __getattr__(self, attr):
		try:
			return list.__getattribute__(self, attr)
		except AttributeError:
			return _CallList( x.__getattribute__(attr) for x in self )

	def where(self, attr, value):
		return next((x for x in self if x.__getattribute__(attr) == value), None)




if __name__ == '__main__':
	#TEST1
	a = ProxyList(('aa',11,'cc'))
	print a.find('a')
	print a[0].__class__ == str
	print a.where('__class__',str)
	#TEST2
	b = ProxyList(('aa','dd','cc'))
	print b.find('d')