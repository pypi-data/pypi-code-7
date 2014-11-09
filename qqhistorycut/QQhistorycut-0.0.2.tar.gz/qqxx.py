#!/usr/bin/env python
#coding=utf-8
import re
import os
class qq_message:
	'''
		@page: history file
		@path: place that user history message save in
 		def __init__(self,page,path)
		def do(self)		
	'''
	def __init__(self,page,path):
		self.page=page
		self.path=path.rstrip('/')
		if os.path.isdir(path+'/user/')==0:
			os.mkdir(path+'/user/')
	def do(self):
		res='\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}\s.*[(<].*[)>]'
		filename=None
		for i in page:
			tmp=re.findall(res,i)
			if(len(tmp)>0):
				filename=re.findall('[(<].*[>)]',tmp[0])
		 		with open(path+'/user/%s'%filename,'w') as writ:
					pass
		 		with open(path+'/user/%s'%filename,'a') as writ:
					writ.write(i)
			elif(filename!=None):
		 		with open(path+'/user/%s'%filename,'a') as writ:
					writ.write(i)
