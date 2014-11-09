
import os
import datetime


class Xymon(object):

	clear = 4
	green = 1
	purple = 2
	yellow = 4
	red = 3

	""" Xymon monitoring object """
	def __init__(self,
		test='testname',
		color='green',
		hostname='localhost',
		text= " ",
		title='Some Test',
		ttl='60',
		my_type='status',
		dont_moan=1,
		debug=0,
		*args,
		**kwargs
		):

		super(Xymon, self).__init__()
		self.test = str(test)
		self.color = color
		self.hostname = hostname
		self.text = text
		self.title = title
		self.ttl = ttl
		self.my_type = my_type
		self.dont_moan = dont_moan
		self.debug = debug
		for key, value in kwargs.iteritems():
			print "%s = %s" % (key, value)

		self.XYMON = os.environ.get('XYMON')
		self.XYMSRV = os.environ.get('XYMSRV')

		if self.XYMON == None:
			self.XYMON = os.environ.get('BB')
		if self.XYMSRV == None:
			self.XYMSRV = os.environ.get('BBDISP')

		if self.XYMON == None:
			self.XYMON = "/opt/xymon/server/bin/bb"
			self.debug = 1
		if self.XYMSRV == None:
			# self.XYMSRV = self.hostname
			self.XYMSRV = "localhost"

	def send(self, *args, **kwargs):
		self.report = self.my_type + " " + self.hostname + "." + self.test
		self.msg = self.report  + " " + self.text
		command = str(self.XYMON) + " " + str(self.XYMSRV) + " " + str(self.msg)
		if self.debug :
			print self.print_debug()
			print command
		else:
			os.system(command)
		result = 1
		return result

	def add_color(self, *args, **kwargs):
		result = 1
		return result

	def color_print(self, *args, **kwargs):
		result = 1
		return result

	def color_line(self, *args, **kwargs):

		result = 1
		return result

	def print_line(self, *args, **kwargs):
		self.text += '\n'
		for s in args:
			self.text += str(s) + ""
		pass

	def print_debug(self, *args, **kwargs):

		print "TEST : " + self.test
		print "COLOR : " + self.color
		print "HOSTNAME : " + self.hostname
		print "TEXT : " + self.text
		print "TITLE : " + self.title
		print "TTL : " + self.ttl
		print "MY_TYPE : " + self.my_type
		for i in args:
			print i
		for key, value in kwargs.iteritems():
			print "%s : %s" % (key, value)
		result = 1
		return result

