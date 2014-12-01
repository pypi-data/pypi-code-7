from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.network import disconnect_all
from fabric.context_managers import settings
from itertools import count

import os
import shutil
import time
#--------------preset--------------
#env.hosts = ['root@192.168.0.69']
#env.password = 'rahasiakita'
#env.base_dir = "root"
#env.domain = "Ipan"
#env.base_domain = "/%(basedir)s/%(domain_name)s" % {'basedir': env.base_dir, 'domain_name':env.domain}
#env.base_local = "blog/project"
#env.base_remote = env.base_domain
#----------------------------------
#env.hosts = ['root@192.168.0.69']
#env.password = 'rahasiakita'
#base_dir = "root"
#domain = "Ipan"
#base_local = "blog/project"
def newfile(param1, param2, user, idtask):
	try:
		with cd(env.base_remote):
			location = param1.encode('string_escape')
			with cd(location):
				run('touch '+param2)
				cmd= user+" run touch newfile named as "+param2+ " in "+env.base_remote+'/'+location
				write_log(cmd)
	except:
		cmd= user+" Failed run touch newfile "+param2+" in "+env.base_remote+'/'+location
		write_log(cmd)
		return run().failed
def copy(param1, param2, user, idtask):
	try:
		run('cp '+env.base_local+'/'+param2+ ' '+env.base_remote+'/'+param1)
		cmd= user+" run copy "+param2+" from "+env.base_local+ " to "+env.base_remote+'/'+param1
		write_log(cmd)
	except:
		cmd= user+" Failed run copy "+param2+" from "+source+" to "+env.base_remote+'/'+param1
		write_log(cmd)
		return run().failed
def deldir(param1, param2, user, idtask):
	try:
		with cd(env.base_remote):
			location = param1.encode('string_escape')
			with cd (location):
				run('rm -r '+param2)
				cmd= user+" run delete directory "+param2+ " in "+env.base_remote+'/'+location
				write_log(cmd)
	except:
		cmd= user+" Failed run delete directory "+param2+" in "+env.base_remote+'/'+location
		write_log(cmd)
		return run().failed
def delfile(param1, param2, user, idtask):
	try:
		with cd(env.base_remote):
			location = param1.encode('string_escape')
			with cd (location):
				run('rm '+param2)
				cmd= user+" run remove file "+param2+ " in "+env.base_remote+'/'+location
				write_log(cmd)
	except:
		cmd= user+" Failed run remove file "+param2+" in "+env.base_remote+'/'+location
		write_log(cmd)
		return run().failed		
def mkdir(param1, param2, user, idtask):
	try:
		with cd(env.base_remote):
			location = param1.encode('string_escape')
			with cd(location):
				run('mkdir '+param2)
				cmd= user+" run make directory "+param2+" in "+env.base_remote+"/"+location
				write_log(cmd)
	except:
		cmd= user+" Failed run make directory "+param2+" in "+env.base_remote+"/"+location
		write_log(cmd)
		return run().failed	
def uploadfile(param1, param2, user, idtask):
	try:
		put(env.base_local+'/'+param2 ,env.base_remote+'/'+param1)
		cmd= user+" upload file "+param2+" from "+env.base_local+" to "+env.base_remote+'/'+param1
		write_log(cmd)
	except:
		cmd= user+" Failed run upload file "+param2+" from "+env.base_local+" to "+env.base_remote+'/'+param1
		write_log(cmd)
		return run().failed
#def uploadfilex(param1, param2, user):
#	with cd('/root/Ipan'):
#		inicoba = 'inicoba'
#		run('mkdir -p '+inicoba)
#		with cd(inicoba):
#			foldernya = 'inicobawith2'
#			run('mkdir -p '+foldernya)
#		run('cp --parent -avr tea/a '+inicoba+'/'+foldernya)
def write_log(command):
	times = time.strftime("%c")
	setting = "(setting host: "+hostnya+" base domain: "+env.base_domain+")" 
	log_write = command+' '+times+' '+setting+'\n'
	file = open('log/log.dj','a')
	file.write(log_write)
	file.close()
def write_errorlog():
	times = time.strftime("%c")
	log_write = 'an error has occurred, do rollback on '+times+'\n'
	file = open('log/log.dj','a')
	file.write(log_write)
	file.close()
def createbackup(param1, param2, idtask, base_remote):
	if (env.base_remote == ''):
		env.base_remote = base_remote
	with cd(env.base_remote):
		run('mkdir -p temp')
		temp = 'temp'
		with cd(temp):
			tempfoldercommand = temp+'_'+idtask
			run('mkdir -p '+tempfoldercommand)
		run('[ -e '+param1+'/'+param2+' ] && cp --parent -avr '+param1+'/'+param2+' temp/'+tempfoldercommand+'|| true') 
def createtempexecbackup(param1, param2, idtask, base_remote):
	if (env.base_remote == ''):
		env.base_remote = base_remote
	with cd (env.base_remote):
		run ('mkdir -p temp')
		temp = 'temp'
		with cd (temp):
			tempfoldercommand = temp+'_'+idtask
			run('mkdir -p '+tempfoldercommand)
			with cd(tempfoldercommand):
				run('mkdir -p '+temp)
		run ('[ -e '+param1+'/'+param2+' ] && cp --parent -avr '+param1+'/'+param2+' temp/'+tempfoldercommand+'/'+temp+'|| true')
def dorevert (param1, param2, idtask, base_remote):
	if (env.base_remote == ''):
		env.base_remote = base_remote
		tempfoldercommand = 'temp_'+idtask
		with cd(env.base_remote):
			run('[ -e temp/'+tempfoldercommand+'/'+param1+'/'+param2+' ] && cp -avr temp/'+tempfoldercommand+'/'+param1+'/'+param2+' '+param1+'||rm -rf '+param1+'/'+param2)
	else :
		tempfoldercommand = 'temp_'+idtask
		with cd(env.base_remote):
			run('[ -e temp/'+tempfoldercommand+'/'+param1+'/'+param2+' ] && cp -avr temp/'+tempfoldercommand+'/'+param1+'/'+param2+' '+param1+'||rm -rf '+env.base_remote+'/'+param1+'/'+param2)
		
def dorollbackexecutefail (param1, param2, idtask, base_remote):
	if (env.base_remote == ''):
		env.base_remote = base_remote
		tempfoldercommand = 'temp_'+idtask
		with cd(env.base_remote):
			run('[ -e temp/'+tempfoldercommand+'/temp/'+param1+'/'+param2+' ] && cp -avr temp/'+tempfoldercommand+'/temp/'+param1+'/'+param2+' '+param1+'||rm -rf '+param1+'/'+param2)#Alpha
	else :
		tempfoldercommand = 'temp_'+idtask
		with cd(env.base_remote):
			run('[ -e temp/'+tempfoldercommand+'/temp/'+param1+'/'+param2+' ] && cp -avr temp/'+tempfoldercommand+'/temp/'+param1+'/'+param2+' '+param1+'||rm -rf '+env.base_remote+'/'+param1+'/'+param2)

def preset(hostname, username, password, basepath, localbasepath):
	global hostnya
	hostnya = username+"@"+hostname
	env.hosts = [hostnya]
	env.password = password
	env.base_domain = basepath
	env.base_local = localbasepath.encode('string_escape')
	env.base_remote = env.base_domain
	#cmd = "do preset to "+username+"@"+hostname+" with basepath "+basepath
	#write_log(cmd)
def default():
	env.base_local = "blog/project"
	env.base_remote = env.base_domain
def list():
	preset()
	run ('ls '+env.base_domain)
def docommand(command, user):
	run (command)
	
	cmd= user+" do custom command: '"+command+"'"
	write_log(cmd)

#ini tahap coba coba
#def removefile (namafile, user):
#	with settings(warn_only = True): 
		#with cd(base_dir): 
		#run('rm '+namafile)
#		result=run('rm '+namafile)
#		if result.failed: 
			#cmd= user+" Success run remove file "+namafile+ " in "+base_dir
#			cmd= user+" Failed run remove file "+namadokumen+" to "+base_dir+'/'+destination 
#		else : 
			#cmd= user+" Failed run remove file "+namadokumen+" to "+base_dir+'/'+destination
#			cmd= user+" Success run remove file "+namafile++ " in "+base_dir			
#		write_log(cmd)

#def removefile (namafile, user):
#	try:
#		with cd(base_dir):
#			run('rm '+namafile)
#			cmd= user+" Success run remove file "+namafile+ " in "+base_dir
#			write_log(cmd)
#	except:
#		cmd= user+" Failed run remove file "+namafile+" in "+base_dir+">> Do rollback"
#		write_log(cmd)
#		return run().failed
			
#def removefile (namafile, user):
#	command = 
#	if run ('rm '+namafile).failed:
#		cmd =user+" Failed run remove file "+namafile
#		
#	else:
#		cmd =user+" Success run remove file "+namafile
#	write_log(cmd)	

#def backup():
#	run ('mkdir -p temp')
#	run ('cp -avr '+env.base_domain+' temp')
	
#def delbackup():
#	run('rm -r temp')
#def delproject():
#	run('rm -r '+env.domain)
#def copyfromtemp():
#	with cd('temp'):
#		run('cp -avr '+env.domain+' /'+env.base_dir)