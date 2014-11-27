#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tiger, cStringIO
from user import User
from base64 import *
class ProtocolHandler:
	
	def __init__(self, client):
		self.client = client
	
	def processcommand(self, message):
		strtype = ""
		command = ""
		parameter = ""
		
		try:
			strtype = message[0:1]
			command = message[1:4]
			parameter = message[message.find(" ")+1:]
		except:
			command = message
			parameter = ""

		param = None
		if command == "INF":
			"""
			Client information string, sent for all users on login, and when new users joins
			INF <CID> <field1> <field2> … <fieldN>
			Types: B, C, I
			States: IDENTIFY, NORMAL
			"""
			if strtype == "I":
				self.doiinf(parameter)
			else:
				param = parameter.split(" ", 1)
				self.doinf(param[0], param[1])
		elif command == "MSG":
			if strtype == "B":
				self.domsg(parameter)
			else:
				self.doemsg(parameter)
		elif command == "LIV":
			self.doalivemessage(parameter)
		elif command == "STA":
			self.dostatusmessage(parameter)
		elif command == "SUP":
			self.dosupports(parameter)
		elif command == "QUI":
			# Specified user has exited the hub
			# QUI <CID> <reason> <param1>…<paramN> <message>
			if parameter.find(" ") > 0:
				self.doquipar(parameter.split(" "))
			else:
				self.doqui(parameter)
		elif command == "SID":
			self.dosid(parameter)
		elif command == "GPA":
			# A password is required, nick is probably registered
			# GPA <data>
			self.dogetpass(parameter)
		#elif command == "SCH":
			# Search sent from other clients, most common protocol message
			# SCH <my-CID> <field1> <field2> … <fieldN>
			# Types: P,U,D,(B)
			#self.dosearch(parameter)
		#elif command == "RES":
			#Searchresult sent back if passive
			#RES <my-CID> <field1> <field2> … <fieldN>
			#Types: D, U
			#self.dosch(parameter)
		#elif command == "CTM":
			# Another client wants us to initiate client to client connection (active users)
			#* CTM <my-CID> <token> <proto> <port>
			#* Types: D
			#self.doctm(parameter)
		#elif command == "RCM":
			# Another client wants us to ask them to initiate client to client connection (passive users)
			#* RCM <my-CID> <token> <proto>
			#* Types: D
			#self.dorcm(parameter)
		#elif command == "CMD":
			#self.dousercommand(parameter)
		elif command == "$Lo":
			return
		else:
			self.domsg(message)
	
	def dcdecode(self, text):
		text = text.replace("\\\\", "\\")
		text = text.replace("\\s", " ")
		text = text.replace("\\n", "\n")
		return text
	
	def dcencode(self, text):
		text = text.replace("\\", "\\\\")
		text = text.replace("\n", "\\n")
		text = text.replace(" ", "\\s")
		return text
	
	def dooplist(self, user):
		self.client.nicklist.setoperators(user.sid)
	
	def doinf(self, sid, parameter):
		newuser = False
		isme = False
		sendbinf = "BINF " + sid
		if sid == self.client.sid:
			isme = True
		user = self.client.nicklist.get(sid)
		if user.username == "":
			newuser = True
		p = parameter.split(" ")
		isflag = False
		for item in p:
			isflag = False
			prefix = item[0:2]
			if prefix == "I4":
				# IPv4 address without port. A zero address (0.0.0.0) means that the server should replace it with the real IP of the client.
				user.ip = item[2:len(item)]
				if isinstance(self.client.events, dict):
					if 'oniprecvd' in self.client.events:
						self.client.events['oniprecvd'](self.client.clientinfo.hubaddress())
				else:
					if 'oniprecvd' in dir(self.client.events):
						self.client.events.oniprecvd(self.client.clientinfo.hubaddress(), user.sid, user.ip)
			#elif prefix == "I6":
				# IPv6 address without port. A zero address ([0:0:0:0:0:0:0:0]) means that the server should replace it with the real IP of the client.
			elif prefix == "U4":
				# Client UDP port. Sending this field to the hub with a port means that this client wants to run in active mode for UDP. If this field is missing (or empty if changing modes), it means that the client should be treated as passive
				user.port = int(item[2:len(item)])
			#elif prefix == "U6":
				# Same as U4 but for IPv6
			elif prefix == "ID":
				# Client ID of user
				user.cid = item[2:len(item)]
			elif prefix == "SS":
				#Share size in bytes, integer
				user.sharesize = int(item[2:len(item)])
			elif prefix == "SF":
				# Number of shared files, integer
				user.sharedfiles = int(item[2:len(item)])
			elif prefix == "VE":
				# Client identification, version (client specific, recommended a short identifier then a float for version number). It is important that hubs don’t discriminate clients based on their VE tag but instead rely on SUP when it comes to which clients should be allowed (for example, “we only want clients that can hash”). VE is there mainly for informative reasons, and can perhaps be used to warn users that they’re using a known buggy or vulnerable client.
				user.tag = self.dcdecode(item[2:len(item)])
			elif prefix == "US":
				# Max upload speed bits/sec, integer
				user.maxuploadspeed = int(item[2:len(item)])
			elif prefix == "SL":
				# Upload slots open, integer
				user.openslots = int(item[2:len(item)])
			elif prefix == "AS":
				# Automatic slot allocator speed limit, bytes/sec, integer. This is the recommended method of slot allocation, the client keeps opening slots as long as its total upload speed doesn’t exceed this value. SL then serves as a minimum number of slots open.
				user.autoslots = int(item[2:len(item)])
			elif prefix == "AM":
				# Maximum number of slots open in automatic slot manager mode, integer.
				user.maxopenslots = int(item[2:len(item)])
			elif prefix == "EM":
				# email, string
				user.email = item[2:len(item)]
			elif prefix == "NI":
				# Nickname, string. Hub must ensure that this is unique (case insensitive) in each hub, to avoid confusion. Valid are all displayable characters (char code > 32) apart from space, although hubs are free to limit this further as they like with an appropriate error message.
				user.username = item[2:len(item)]
			elif prefix == "DE":
				# Description, string. Valid are all displayable characters (char code >= 32).
				user.description = self.dcdecode(item[2:len(item)])
			elif prefix == "HN":
				# Hubs where user is a normal user, integer
				user.hubsnormal = int(item[2:len(item)])
			elif prefix == "HR":
				# Hubs where user is registered (had to supply password), integer.
				user.hubsreg = int(item[2:len(item)])
			elif prefix == "HO":
				# Hubs where user is op in, integer
				user.hubsop = int(item[2:len(item)])
			elif prefix == "TO":
				# Token (used with CTM) in the c-c connection.
				user.token = item[2:len(item)]
			elif prefix == "CT":
				# 1=bot, 2=registered user, 4=operator, 8=super user, 16=hub owner, 32=hub (used when the hub sends an INF about itself). Multiple types are specified by adding the numbers together.
				ct = int(item[2:len(item)])
				user.hubstatus = ct
				if ct >= 5:
					user.hubsop += 1
					if isme:
						sendbinf += " HO" + str(user.hubsop)
				elif ct == 2:
					user.hubsreg += 1
					if isme:
						sendbinf += " HR" + str(user.hubsreg)
				elif ct == 0:
					user.hubsnormal += 1
					if isme:
						sendbinf += " HN" + str(user.hubsnormal)
			elif prefix == "OP":
				# 1 = op
				if len(item) > 2:
					if item.strip()[2:] == "1":
						isflag = True
					user.isoperator = isflag
					if isflag:
						self.dooplist(user)
			elif prefix == "AW":
				# 1 = Away Other away modes reserved for the future
				if len(item) > 2:
					if item[2:] == "1":
						isflag = True
					user.isaway = isflag
			elif prefix == "BO":
				# 1 = Bot
				if len(item) > 2:
					if item[2:] == "1":
						isflag = True
					user.isbot = isflag
			elif prefix == "HI":
				# 1 = Hidden
				if len(item) > 2:
					if item[2:] == "1":
						isflag = True
					user.ishidden = isflag
			elif prefix == "SU":
				if len(item) > 2:
					user.supportlist.append(item[2:len(item)])
		self.client.nicklist.adduser(user)
		if isme and len(sendbinf) > 11:
			if self.client.isconnected == False:
				if isinstance(self.client.events, dict):
					if 'onconnected' in self.client.events:
						self.client.events['onconnected'](self.client.clientinfo.hubaddress())
				else:
					if 'onconnected' in dir(self.client.events):
						self.client.events.onconnected(self.client.clientinfo.hubaddress())
			self.client.sendrawmessage(sendbinf + "\n")
			self.client.isconnected = True
		if newuser and self.client.isconnected:
			if isinstance(self.client.events, dict):
				if 'onjoin' in self.client.events:
					self.client.events['onjoin'](self.client.clientinfo.hubaddress(), user.username)
			else:
				if 'onjoin' in dir(self.client.events):
					self.client.events.onjoin(self.client.clientinfo.hubaddress(), user.username)

	def doemsg(self, parameter):
		mess = parameter.split(" ")
		u = self.client.nicklist.get(mess[0])
		if u.sid == self.client.sid:
			return
		u.replyto = u.sid
		text = ""
		text = self.dcdecode(mess[2])
		if u.username != "":
			if len(mess) == 5 and mess[4] == "ME1":
				if isinstance(self.client.events, dict):
					if 'onprivateemote' in self.client.events:
						self.client.events['onprivateemote'](self.client.clientinfo.hubaddress(), u, text)
				else:
					if 'onprivateemote' in dir(self.client.events):
						self.client.events.onprivateemote(self.client.clientinfo.hubaddress(), u, text)
			elif len(mess) == 4:
				if isinstance(self.client.events, dict):
					if 'onprivatemessage' in self.client.events:
						self.client.events['onprivatemessage'](self.client.clientinfo.hubaddress(), u, text)
				else:
					if 'onprivatemessage' in dir(self.client.events):
						self.client.events.onprivatemessage(self.client.clientinfo.hubaddress(), u, text)

	def domsg(self, message):
		mess = message.split(" ")
		u = self.client.nicklist.get(mess[0])
		text = self.dcdecode(mess[1])
		if u.username != "":
			if len(mess) == 3 and mess[2] == "ME1":
				if isinstance(self.client.events, dict):
					if 'onpublicemote' in self.client.events:
						self.client.events['onpublicemote'](self.client.clientinfo.hubaddress(), u, text)
				else:
					if 'onpublicemote' in dir(self.client.events):
						self.client.events.onpublicemote(self.client.clientinfo.hubaddress(), u, text)
			elif len(mess) == 2:
				if isinstance(self.client.events, dict):
					if 'onpublicmessage' in self.client.events:
						self.client.events['onpublicmessage'](self.client.clientinfo.hubaddress(), u, text)
				else:
					if 'onpublicmessage' in dir(self.client.events):
						self.client.events.onpublicmessage(self.client.clientinfo.hubaddress(), u, text)

	def doqui(self, parameter):
		user = self.client.nicklist.get(parameter)
		if user:
			if isinstance(self.client.events, dict):
				if 'onpart' in self.client.events:
					self.client.events['onpart'](self.client.clientinfo.hubaddress(), user.username)
			else:
				if 'onpart' in dir(self.client.events):
					self.client.events.onpart(self.client.clientinfo.hubaddress(), user.username)
			if user.isoperator:
				self.client.nicklist.removeoperator(user.sid)
			self.client.nicklist.removebyclass(user)
	
	def doredirect(self, parameter):
		if self.client.clientinfo.followredirects:
			self.client.disconnect()
			self.client.clientinfo.hubaddress(parameter)
			if isinstance(self.client.events, dict):
				if 'onredirect' in self.client.events:
					self.client.events['onredirect'](self.client.clientinfo.hubaddress())
			else:
				if 'onredirect' in dir(self.client.events):
					self.client.events.onredirect(self.client.clientinfo.hubaddress())
			self.client.connect()
	
	def doquipar(self, par):
		for item in par:
			if item.startswith("MS"):
				#Message
				self.domsg(self.dcdecode(item[2:len(item)]))
			elif item.startswith("RD"):
				# redirect server url
				self.doredirect(item[2:len(item)])
			#elif item.startswith("ID"):
				#SID of the person who kicked the client.
			#elif item.startswith("TL"):
				# Time Left until reconnect is allowed in seconds. -1 = forever
			#elif item.startswith("DI"):
				# Any client that has this flag in the QUI message should have its transfers terminated by other clients connected to it, as it is unwanted in the system.
	
	def dosupports(self, parameter):
		supports = parameter.split(" ")
		supportlist = []
		for item in supports:
			if item.startswith("AD"):
				supportlist.append(item[2:len(item)])
			elif item.startswith("RM"):
				supportlist.remove(item[2:len(item)])
		self.client.hubinfo.hubsupports = supportlist
	
	def dogetpass(self, passkey):
		out = cStringIO.StringIO()
		data = unicode(self.client.clientinfo.password, 'utf8')
		out.write(data)
		data = b32decode(passkey)
		out.write(data)
		th = tiger.new(out.getvalue())
		final = b32encode(th.digest())
		self.client.sendrawmessage("HPAS " + final[0:final.find("=")])
		if isinstance(self.client.events, dict):
			if 'onpassword' in self.client.events:
				self.client.events['onpassword'](self.client.clientinfo.hubaddress())
		else:
			if 'onpassword' in dir(self.client.events):
				self.client.events.onpassword(self.client.clientinfo.hubaddress())
	
	def dosid(self, parameter):
		self.client.sid = parameter
		strpid = self.client.clientinfo.pid()
		u = self.client.nicklist.get(parameter)
		u.cid = self.client.clientinfo.cid()
		u.username = self.client.clientinfo.username
		u.description = self.client.clientinfo.description
		u.ip = self.client.clientinfo.clientip()
		u.port = self.client.clientinfo.clientport
		u.tag = self.client.clientinfo.tag
		self.client.nicklist.adduser(u)
		binf = "BINF {0} ID{1} PD{2} ".format(self.client.sid, u.cid[0:u.cid.find("=")], strpid[0:strpid.find("=")])
		binf += "I4{0} U4{1} SS{2} SF{3} ".format(u.ip, u.port, u.sharesize, u.sharedfiles)
		binf += "VE{0} SL{1} ".format(u.tag.replace(" ", "\\s"), u.openslots+1)
		binf += "NI{0} DE{1} ".format(u.username.replace(" ", "\\s"), u.description.replace(" ", "\\s"))
		binf += "HN{0} HR{1} HD{2}\n".format(u.hubsnormal, u.hubsreg, u.hubsop)
		self.client.sendrawmessage(binf)
	
	def dostatusmessage(self, parameter):
		status = parameter.split(" ")
		scode = int(status[0])
		if scode < 200:
			if isinstance(self.client.events, dict):
				if 'onstatusmessage' in self.client.events:
					self.client.events['onstatusmessage'](self.client.clientinfo.hubaddress(), scode, status[1])
			else:
				if 'onstatusmessage' in dir(self.client.events):
					self.client.events.onstatusmessage(self.client.clientinfo.hubaddress(), scode, status[1])
		elif scode == 200:
			return
		elif scode < 300:
			if scode == 223:
				if isinstance(self.client.events, dict):
					if 'onbadpass' in self.client.events:
						self.client.events['onbadpass'](self.client.clientinfo.hubaddress())
				else:
					if 'onbadpass' in dir(self.client.events):
						self.client.events.onbadpass(self.client.clientinfo.hubaddress())
			else:
				if isinstance(self.client.events, dict):
					if 'onstatusmessage' in self.client.events:
						self.client.events['onstatusmessage'](self.client.clientinfo.hubaddress(), scode, status[1])
				else:
					if 'onstatusmessage' in dir(self.client.events):
						self.client.events.onstatusmessage(self.client.clientinfo.hubaddress(), scode, status[1])
				if self.client.clientinfo.do_ssl:
					self.client.sslsock.disconnect()
				else:
					self.client.sckdata.disconnect()
				return
	
	def doalivemessage(self, parameter):
		#ILIV token
		token = parameter[2:len(parameter)]
		self.client.sendalive(token)
	
	def doiinf(self, parameter):
		param = parameter.split(" ")
		for p in param:
			if p[0:2] == "NI": # Hub name
				self.client.hubinfo.hubname = self.dcdecode(p[2:len(p)])
				if self.dcdecode(p[2:len(p)]) != " ":
					if isinstance(self.client.events, dict):
						if 'onhubname' in self.client.events:
							self.client.events['onhubname'](self.client.clientinfo.hubaddress(), self.client.hubinfo.hubname)
					else:
						if 'onhubname' in dir(self.client.events):
							self.client.events.onhubname(self.client.clientinfo.hubaddress(), self.client.hubinfo.hubname)
			elif p[0:2] == "DE": # Topic
				self.client.hubinfo.topic = self.dcdecode(p[2:len(p)])
				if isinstance(self.client.events, dict):
					if 'ontopic' in self.client.events:
						self.client.events['ontopic'](self.client.clientinfo.hubaddress(), self.client.hubinfo.topic)
				else:
					if 'ontopic' in dir(self.client.events):
						self.client.events.ontopic(self.client.clientinfo.hubaddress(), self.client.hubinfo.topic)
			elif p[0:2] == "VE": # Hub Version
				self.client.hubinfo.hubversion = self.dcdecode(p[2:len(p)])
			#elif p[0:2] == "RE": # Redirect
