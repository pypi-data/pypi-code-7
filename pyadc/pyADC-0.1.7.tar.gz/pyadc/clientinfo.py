#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from datetime import timedelta
from urlparse import urlparse
from base64 import *
import re, tiger, socket, urllib

class ClientInfo:

	class Sharesize(Enum):
		Empty = 0
		Small = 10
		Medium = 50
		Large = 100	
	
	def __init__(self):
		self.hostname = ""
		self.do_ssl = False
		self.port = 0
		self.username = ""
		self.password = ""
		self.description = ""
		self.email = ""
		self.tag = "pyADC"
		self.reconnectondisconnect = False
		self.share = self.Sharesize.Empty
		self.followredirects = False
		self.respondtorevconnecttome = False
		self.clientport = 1337
		self.client_pid = ""
		self.client_cid = ""
		
	def clientip(self):
		url = "http://checkip.dyndns.org"
		request = urllib.urlopen(url).read()
		theIP = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}", request)
		return theIP[0]
	
	def pid(self, newpid=""):
		if newpid != "": # Set PID
			self.client_pid = newpid
			data = b32decode(self.client_pid)
			th = tiger.new(data)
			self.client_cid = b32encode(th.digest())
		elif newpid == "": # Get PID
			if self.client_pid != "":
				return self.client_pid
			with open('/proc/uptime', 'r') as f:
				for line in f:
					uptime_seconds = float(line.split()[0])
			data = tiger.new(unicode(socket.gethostname()+"pyADC"+str(uptime_seconds), 'utf8')).digest()
			final = b32encode(data)
			self.client_pid = final
			return self.client_pid

	def cid(self):
		if self.client_cid != "":
			return self.client_cid
		else:
			if self.client_pid != "":
				data = b32decode(self.client_pid)
				th = tiger.new(data)
				self.client_cid = b32encode(th.digest())
				return self.client_cid
			else:
				self.pid()
				self.cid()
	
	def hubaddress(self, address=""):
		if address == "": # Get
			return "{0}:{1}".format(self.hostname, str(self.port))
		elif address != "": # Set
			parseit = urlparse(address)
			if parseit.scheme == "" and parseit.netloc == "":
				return
			if parseit.scheme == "adcs":
				self.do_ssl = True
			self.hostname = parseit.hostname
			self.port = parseit.port
	
