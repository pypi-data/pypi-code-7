#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum

class User:
	
	class CT(Enum):
		nill = 0
		bot = 1
		user = 2
		op = 4
		suser = 8
		owner = 16
		hub = 32
	
	def __init__(self):
		self.ip = ""
		self.port = 0
		self.speed = ""
		self.sharesize = 0
		self.sharedfiles = 0
		self.tag = ""
		self.maxuploadspeed = 0
		self.openslots = 0
		self.autoslots = 0
		self.maxopenslots = 0
		self.email = ""
		self.username = ""
		self.description = ""
		self.hubsnormal = 0
		self.hubsreg = 0
		self.hubsop = 0
		self.hubsstatus = self.CT.nill
		self.sid = ""
		self.cid = ""
		self.token = ""
		self.isoperator = False
		self.ishidden = False
		self.isbot = False
		self.isaway = False
		self.supportlist = []
		self.downloadlist = []
		self.replyto = ""
		self.logintime = 0
