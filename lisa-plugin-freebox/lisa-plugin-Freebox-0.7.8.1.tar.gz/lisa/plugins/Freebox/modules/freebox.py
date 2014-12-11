# -*- coding: UTF-8 -*-

#	"ids" : "donnes infos", 
#	"meth" : "switch",
#	"idx" : "ok|ok",
#	"idx_sec" : "2",
#	"boy" : "Voici les info du progamme"
# 
# # 	param à faire ip et port
# # 	param à faire multiplayer
#
from lisa.server.plugins.IPlugin import IPlugin
from twisted.python import log
import gettext
import inspect
import os
import requests
import json
import time

# Code zappette
code_Fb= "35782633"
log.msg("*************  FREEBOX ****************")

class Freebox(IPlugin):
	def __init__(self):
		super(Freebox, self).__init__()
		self.configuration_plugin = self.mongo.lisa.plugins.find_one({"name": "Freebox"})
		self.path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(
		inspect.getfile(inspect.currentframe()))[0],os.path.normpath("../lang/"))))
		self._ = translation = gettext.translation(domain='freebox',
			localedir=self.path,
			languages=[self.configuration_lisa['lang']]).ugettext
#
	def switch(self, jsonInput):
		rangs = [] 
		bodies = ""
		entity = jsonInput['outcome']['intent']
		log.msg("entity :  %s" % (entity))
		ent = entity[:5]		
		if ent == "Fb_Ch" :
			on_off = "ONOFF"
			location = "VIDE"
		else ent == "Fb_info" :
			on_off = "ONOFF"
		#	location = "VIDE"
		else ent == "Fb_son" :
		#	on_off = "ONOFF"
			location = "VIDE"
#
		idex= entity + "_" + location + "_" + on_off
		log.msg("index :  %s" % (idex))	
#		
		for rs in self.configuration_plugin['param_fb']:
			log.msg(" rs  :  %s" % (rs))
			log.msg("ids  :  %s" % (rs['ids']))
			if rs['ids'] == idex :
				log.msg("*************  TROUVé ****************")
				log.msg("idx  :  %s" % (rs['idx']))
				log.msg("idx sec :  %s" % (int(rs['idx_sec'])))
				log.msg(" boy  :  %s" % (rs['boy']))
				bodies = rs['boy']
				log.msg("BODIES  :  %s" % (bodies))
				if rs['idx_sec'] == "2":
					log.msg("*************  'idx_sec'] <> 1 ****************")
					# séparation de rs['idx'], nombre   len(maliste)
					lg=len(rs['idx'])		
					log.msg(" lg  :  %s" % (lg))
					for bar in range(lg):
##				#	while i = rs['idx_sec']:
##						for i in rs['idx_sec']:
						if rs['idx'][bar] == '|':
							log.msg(" bar  :  %s" % (bar))
							ind1 = rs['idx'][:bar]
							ind2 = rs['idx'][bar+1:]
							log.msg(" ind1  :  %s" % (ind1))
							log.msg(" ind2  :  %s" % (ind2))
##>>> x[2:]
##'llo World!'
##>>> x[:2]
##'He'
##>>> x[:-2]
##'Hello Worl'
##>>> x[-2:]
##'d!'
##>>> x[2:-2]
##'llo Worl'
							resp = requests.get ('http://hd2.freebox.fr/pub/remote_control?code=%s&key=%s' % (code_Fb,ind1))
	##						time.sleep(2)		
							resp = requests.get ('http://hd2.freebox.fr/pub/remote_control?code=%s&key=%s' % (code_Fb,ind2))
		##					log.msg("resp  :  %s" % (resp))
				if rs['idx_sec'] == "1":
					log.msg("*************  'idx_sec'] = 1 ****************")
					resp = requests.get ('http://hd2.freebox.fr/pub/remote_control?code=%s&key=%s' % (code_Fb,rs['idx']))
					log.msg("resp unique   :  %s" % (resp))
				
				
		if bodies == "":
			bodies = "j'ai rien compris aux switch"
		return {"plugin": "Freebox",
			"method": "switch",
			"body": bodies
		}

