#!/usr/bin/env python
# -*- coding: utf-8 -*-
import clientinfo, hubinfo, protocol, socket, ssl, threading, nicklist
import errno
from socket import error as socket_error

class Clients:
	
	def __init__(self):
		self.clientlist = []
	
	def addclient(self, cl):
		if isinstance(cl, Client):
			self.clientlist.append(cl)
	
	def delclient(self, cl):
		if isinstance(cl, Client):
			self.clientlist.remove(cl)
	
	def getclientbyaddress(self, hubaddress):
		for cl in self.clientlist:
			if cl.clientinfo.hubaddress() == hubaddress:
				return cl
		return False
	
	def getaddressfromname(self, hubname):
		for cl in self.clientlist:
			if cl.hubinfo.hubname == hubname:
				return cl.clientinfo.hubaddress()
		return False

	def makeclient(self, address, username, password, description, events=None, owner="", pid=""):
		cl = Client()
		cl.clientinfo.hubaddress(address)
		cl.clientinfo.username = username
		cl.clientinfo.password = password
		cl.clientinfo.description = description
		if not isinstance(events, dict):
			cl.events = events
		else:
			if len(events) > 0:
				cl.events = events
		cl.clientinfo.pid(pid)
		cl.owner = owner
		cl.connect()
		self.addclient(cl)
		return cl

class Client:
	
	def __init__(self):
		self.clientinfo = clientinfo.ClientInfo()
		self.hubinfo = hubinfo.HubInfo()
		self.protocol = protocol.ProtocolHandler(self)
		self.nicklist = nicklist.NickList()
		self.sid = ""
		self.owner = ""
		self.isconnected = None
		self.debug = False
		self.events = {}
	
	def sckread(self):
		data = ''
		while 1:
			try:
				data = self.sckfile.readline()
			except socket.timeout:
				if isinstance(self.events, dict):
					if 'ondisconnect' in self.events:
						self.events['ondisconnect'](self.clientinfo.hubaddress())
				else:
					if 'ondisconnect' in dir(self.events):
						self.events.ondisconnect(self.clientinfo.hubaddress())
				if self.clientinfo.reconnectondisconnect:
					self.connect()
			if data == "": break
			if data != "":
				if self.debug:
					print "Receive:> " + data.strip()
				self.protocol.processcommand(data.strip())
	
	def connect(self):
		self.isconnected = False
		self.nicklist.clear()
		self.sckdata = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if self.clientinfo.do_ssl == True:
			self.sckdatassl = ssl.wrap_socket(self.sckdata)
			self.sckdatassl.settimeout(10)
			self.sckdatassl.connect((self.clientinfo.hostname, self.clientinfo.port))
			self.sckdatassl.settimeout(None)
			self.sckfile = self.sckdatassl.makefile()
		else:
			self.sckdata.settimeout(10)
			self.sckdata.connect((self.clientinfo.hostname, self.clientinfo.port))
			self.sckdata.settimeout(None)
			self.sckfile = self.sckdata.makefile()
		if self.debug:
			print "Debug Mode is Active"
		if isinstance(self.events, dict):
			if 'onconnecting' in self.events:
				self.events['onconnecting'](self.clientinfo.hubaddress())
		else:
			if 'onconnecting' in dir(self.events):
				self.events.onconnecting(self.clientinfo.hubaddress())
		self.sendrawmessage("HSUP ADBASE ADTIGR ADALIV ADORLY")
		self.sckthrd = threading.Thread(target=self.sckread)
		self.sckthrd.daemon = True
		self.sckthrd.start()
		
	def disconnect(self):
		if self.clientinfo.do_ssl == True:
			self.sckdatassl.shutdown(socket.SHUT_RDWR)
			self.sckdatassl.close()
		else:
			self.sckdatassl.shutdown(socket.SHUT_RDWR)
			self.sckdata.close()
		self.isconnected = False
		self.nicklist.clear()
		try:
			self.sckthrd.join()
		except:
			print "Error stopping thread."
		
	def sendrawmessage(self, message):
		try:
			if not message.endswith("\n"):
				message += "\n"
			if self.debug:
				print "SEND:> " + message
			if self.clientinfo.do_ssl == True:
				self.sckdatassl.sendall(message)
			else:
				self.sckdata.sendall(message)
		except:
			print "Error trying to send data."
			
	def sendmainchatmessage(self, message, emote=False):
		if message.endswith("\n"):
			message = message[0:len(message)-1]
		if emote:
			msg = "BMSG {0} {1} ME1\n".format(self.sid, self.protocol.dcencode(message))
		else:
			msg = "BMSG {0} {1}\n".format(self.sid, self.protocol.dcencode(message))
		self.sendrawmessage(msg)
	
	def sendprivatemessagebyclass(self, user, message, emote=False):
		if message.endswith("\n"):
			message = message[0:len(message)-1]
		if emote:
			msg = "EMSG {0} {1} {2} PM{0} ME1\n".format(self.sid, user.sid, self.protocol.dcencode(message))
		else:
			msg = "EMSG {0} {1} {2} PM{0}\n".format(self.sid, user.sid, self.protocol.dcencode(message))
		self.sendrawmessage(msg)
	
	def sendprivatemessage(self, username, message, emote=False):
		user = None
		for item in self.nicklist.userlist:
			if item.username == username:
				user = item
		self.sendprivatemessagebyclass(user, message, emote)
	
	def sendprivatemainchatmessagebyclass(self, user, message):
		if message.endswith("\n"):
			message = message[0:len(message)-1]
		msg = "DMSG {0} {1} {2}\n".format(self.sid, user.sid, self.protocol.dcencode(message))
		self.sendrawmessage(msg)
	
	def sendprivatemainchatmessage(self, username, message):
		user = None
		for item in self.nicklist.userlist:
			if item.username == username:
				user = item
		self.sendprivatemainchatmessagebyclass(user, message)
	
	def sendalive(self, token):
		msg = "HLIV {0} TO{1}".format(self.sid, token)
		self.sendrawmessage(msg)
	"""
	def sendsearch(self, searchinfo):
		self.sendrawmessage(searchinfo.tostring())
	
	def sendsearchreply(self, username, searchreply):
		msg = "RES {0} {1} {2}\n".format(self.sid, user, searchreply.tostring())
		self.sendrawmessage(msg)
	
	def sendsearchreplybyclass(self, user, searchreply):
		self.sendsearchreply(user.sid, searchreply)
	"""
	def sendconnecttome(self, user):
		msg = "DCTM {0} {1} {2}\n".format(user.SID, self.clientinfo.clientport, user.token)
		self.sendrawmessage(msg)
	
	def sendrevconnecttome(self, user, ssl):
		proto = "ADC/1.0"
		if ssl:
			proto = "ADCS/0.10"
		msg = "DCRM {0} [1} {2} foobar\n".format(self.sid, user.sid, proto)
		self.sendrawmessage(msg)
	
	
	
