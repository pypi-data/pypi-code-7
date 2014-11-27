#!/usr/bin/env python
# -*- coding: utf-8 -*-
from user import User
class NickList:
	
	def __init__(self):
		self.userlist = []
		self.operators = []
		
	def adduser(self, user):
		if isinstance(user, User):
			if not user in self.userlist:
				self.userlist.append(user)
		else:
			return
	
	def removebyclass(self, user):
		if isinstance(user, User):
			self.userlist.remove(user)
	
	def findbyusername(self, username):
		lst = []
		for item in self.userlist:
			if item.username.lower() == username.lower():
				lst.append(item)
		if len(lst) == 0:
			return False
		elif len(lst) == 1:
			return lst[0]
		else:
			return lst
	
	def findbyip(self, ip):
		lst = []
		for item in self.userlist:
			if item.ip == ip:
				lst.append(item)
		if len(lst) == 0:
			return False
		elif len(lst) == 1:
			return lst[0]
		else:
			return lst
	
	def get(self, sid):
		for item in self.userlist:
			if item.sid == sid:
				return item
		u = User()
		u.sid = sid
		return u
	
	def clear(self):
		del self.userlist[:]
		del self.operators[:]

	def setoperators(self, sid):
		if not sid:
			if not sid in self.operators:
				operators.append(sid)
			for item in self.userlist:
				if item.sid == sid:
					item.isoperator = True

	def removeoperator(self, sid):
		if sid in self.operators:
			self.operators.remove(sid)
