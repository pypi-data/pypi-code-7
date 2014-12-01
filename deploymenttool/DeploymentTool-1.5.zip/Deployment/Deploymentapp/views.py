from django.shortcuts import render
from django.template.response import TemplateResponse
from django.http import *
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from Deploymentapp.models import Hosts,Users,Task,Commands
from django.contrib.auth.decorators import login_required
import os

#----------------------------------------------------------------------------------

#---------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
#def default() :
#	loadhost = Hosts.objects.get(idhosts = '1')
#	global host
#	global basepath
#	host = loadhost.hostname
#	basepath = loadhost.basepath
#----------------------------------------------------------------------------------
def home (request):
	return HttpResponseRedirect("/login/")
#----------------------------------------------------------------------------------
def gethosts(hostname):
	global gethost
	gethost = Hosts.objects.get(hostname = hostname)
	return gethost
#---------------------------------------------------------------------------------
	
#---------------------------------------------------------------------------------
def getusers(usrnm):
	global getuser
	getuser = Users.objects.get(usersname = usrnm)
	return getuser
#---------------------------------------------------------------------------------
	
#---------------------------------------------------------------------------------
def signin(request):
	return TemplateResponse(request, "signin.html")
#---------------------------------------------------------------------------------
	
#---------------------------------------------------------------------------------
def loginattempt(request):
	return TemplateResponse(request, "loginattempt.html")
#---------------------------------------------------------------------------------
	
#---------------------------------------------------------------------------------
@login_required
def tasklist(request):
	get = getusers(request.session['name'])
	request.session['host'] = get.host.hostname
	return TemplateResponse(request, "tasklist.html",{'tasklists' : Task.objects.all(), 'host' : request.session['host'] })
#---------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
@login_required
def loadtask(request,idtask):
	taskload = Commands.objects.filter(idtasks__idtask=idtask) 
	loadtaskname = Task.objects.get(idtask=idtask)
	request.session['host'] = loadtaskname.hostes.hostname
	request.session['task'] = loadtaskname.taskname
	return TemplateResponse(request, "projecttask.html", {'taskloads' : taskload, 'nametask' : loadtaskname })
#---------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
@login_required
def deletetask(request,idtask):
	deleted = Task.objects.get(idtask = idtask)
	deleted.delete()
	return HttpResponseRedirect("/tasklist/")
#---------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
@login_required
def deletecommand(request,idcommand):
	deleted = Commands.objects.get(idcommand = idcommand)
	deleted.delete()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#---------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
@login_required
def deleteallcommand(request):
	query = Task.objects.get(taskname=request.session['task'])
	idtask = query.idtask
	deleted = Commands.objects.filter(idtasks__idtask=idtask)
	for cmd in deleted:
		cmd.delete()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
@login_required
def searchtask(request):
	get = getusers(request.session['name'])
	request.session['host'] = get.host.hostname
	search = request.POST.get('search')
	#query = Task.objects.get(taskname__contains=search)
	return TemplateResponse(request, "search.html",{'tasks' : Task.objects.filter(taskname__contains=search), 'host' : request.session['host'] })
#---------------------------------------------------------------------------------
	
#---------------------------------------------------------------------------------
@login_required
def addproject(request):
	query = Task.objects.get(taskname=request.session['task'])
	idtask = query.idtask
	loadtask(request,idtask)
	return HttpResponseRedirect("/projectload/%s" % query.idtask)
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
def authentication(request):
	request.session['name'] = request.POST['usrname']
	request.session['password'] = request.POST['passwd']
	request.session['counter']=3
	user = authenticate(username = request.session['name'], password = request.session['password'])
	if user is not None and user.is_staff:
		login(request,user)
		users = getusers(request.session['name'])
		if users.host is None : 
			loadhost = Hosts.objects.get(idhosts = '1')
			request.session['host'] = loadhost.hostname
			basepath = loadhost.basepath
			users = getusers(request.session['name'])
			users.save()
		else :
			request.session['host'] = users.host.hostname
		initscript(request)
		initbackupscript(request)
		initrevertscript(request)
		inittempbackupscript(request)
		initrollbackscript(request)
		return HttpResponseRedirect("/tasklist/")
	else :
		return loginattempt(request)
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
@login_required
def loggedout(request):
	try:
		deletescript(request)
		deletebackupscript(request)
		deleterevertscript(request)
		deleterollbackscript(request)
		deletetempbackupscript(request)
		del request.session['name']
		del request.session['password']
		del request.session['task']
		del request.session['host']
		del request.session['counter']
		logout(request)
	except KeyError :
		pass
	return HttpResponseRedirect("/")
#---------------------------------------------------------------------------------
	
#---------------------------------------------------------------------------------
@login_required
def addnewtask(request):
	users = getusers(request.session['name'])
	request.session['host'] = users.host.hostname
	gethostobj = gethosts(request.session['host'] )
	request.session['task'] = request.POST.get('addnew')
	savetask = Task(author = getuser, taskname = request.session['task'], hostes = gethostobj, status = 0, basespath = '')
	savetask.save()
	return HttpResponseRedirect("/projecttask/") 
#--------------------------------------------------------------------------------
def error404(request):
	return render(request, '404.html', status=404)
	#return HttpResponse("page not found")
#--------------------------------------------------------------------------------
@login_required
def changehostuser(request) :
	#global host
	request.session['host'] = request.POST.get('host')
	gethostobj = Hosts.objects.get(hostname = request.session['host'] )
	get = getusers(request.session['name'])
	get.host = gethostobj
	get.save()
	return HttpResponseRedirect("/tasklist/")
#---------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
@login_required
def changehosttask(request) :
	#global host
	request.session['host']  = request.POST.get('hosts')
	gethostobj = Hosts.objects.get(hostname = request.session['host'] )
	get = Task.objects.get(taskname = request.session['task'])
	get.hostes = gethostobj
	get.save()
	return HttpResponseRedirect("/projectload/%s" % get.idtask)
#---------------------------------------------------------------------------------
@login_required
def runedit(request,idcommand):
	get = Commands.objects.get(idcommand = idcommand)
	backs = request.META.get('HTTP_REFERER' )
	if(get.commandname == "newfile")or(get.commandname == "mkdir") or (get.commandname == "delfile")or(get.commandname == "deldir"):
		return TemplateResponse(request, "editparam2.html", {'edit' : get, 'backs' : backs})
	else:
		return TemplateResponse(request, "editparam3.html", {'edit' : get, 'backs' : backs})
@login_required		
def editcommand(request):
	query = Task.objects.get(taskname=request.session['task'])
	id = query.idtask
	taskhost = query.hostes
	gethosts(request.session['host'] )
	idcommand = request.POST['commandname']
	getcommand = Commands.objects.get(idcommand = idcommand)
	basepathstatus = request.POST['basedir']
	if(getcommand.commandname == "uploadfile") or (getcommand.commandname == "copy"):
		getcommand.parameter1 = request.POST["param1"]
		getcommand.parameter2 = request.POST["param2"]
		getcommand.localbasepath = request.POST["localbasepath"]
		if(basepathstatus == "optiondefault"):
			getcommand.basespaths = taskhost.basepath
			getcommand.isdefault = 1
		elif(basepathstatus == "optioncustom"):
			basepath = request.POST["inputbasedir"]
			getcommand.basespaths = basepath
			getcommand.isdefault = 0
		else:
			getcommand.basespaths = ''
			getcommand.isdefault = 0
	else:
		getcommand.parameter1 = request.POST["param1"]
		getcommand.parameter2 = request.POST["param2"]
		if(basepathstatus == "optiondefault"):
			getcommand.basespaths = taskhost.basepath
			getcommand.isdefault = 1
		elif(basepathstatus == "optioncustom"):
			basepath = request.POST["inputbasedir"]
			getcommand.basespaths = basepath
			getcommand.isdefault = 0
		else:
			getcommand.basespaths = ''
			getcommand.isdefault = 0
	getcommand.save()
	return HttpResponseRedirect("/projectload/%s"% getcommand.idtasks.idtask)

#ini block command--------------------------------
@login_required	
def copy(request):
	gethosts(request.session['host'] )
	users = getusers(request.session['name'])
	query = Task.objects.get(taskname=request.session['task'])
	param_a = request.POST['destination']
	param_b = request.POST['location']
	param_c = request.POST['localbasepath']
	basepathstatus = request.POST['basedir']
	command = "copy"
	if(basepathstatus == "optiondefault"):
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = gethost.basepath, localbasepath =param_c, isdefault = 1)
	elif(basepathstatus == "optioncustom"):	
		basepath = request.POST['inputbasedir']
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = basepath, localbasepath = param_c, isdefault = 0)
	else:
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = '', localbasepath = param_c, isdefault = 0)
	addcommand.save()
	return HttpResponseRedirect("/projectload/%s" % query.idtask)
@login_required
def createfile(request):
	gethosts(request.session['host'] )
	users = getusers(request.session['name'])
	query = Task.objects.get(taskname=request.session['task'])
	param_a = request.POST['location']
	param_b = request.POST['namafile']
	basepathstatus = request.POST['basedir']		
	command = "newfile"
	if(basepathstatus == "optiondefault"):
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = gethost.basepath, localbasepath = '', isdefault = 1)
	elif(basepathstatus == "optioncustom"):	
		basepath = request.POST['inputbasedir']
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = basepath, localbasepath = '', isdefault = 0)
	else:
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = '', localbasepath = '', isdefault = 0)
	addcommand.save()
	return HttpResponseRedirect("/projectload/%s" % query.idtask)
@login_required	
def deletedir(request):
	gethosts(request.session['host'] )
	users = getusers(request.session['name'])
	query = Task.objects.get(taskname=request.session['task'])
	param_a = request.POST['location']
	param_b = request.POST['namadir']
	basepathstatus = request.POST['basedir']	
	command = "deldir"
	if(basepathstatus == "optiondefault"):
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = gethost.basepath, localbasepath = '', isdefault = 1)
	elif(basepathstatus == "optioncustom"):
		basepath = request.POST['inputbasedir']
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = basepath, localbasepath = '', isdefault = 0)
	else:
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = '', localbasepath = '', isdefault = 0)
	addcommand.save()
	return HttpResponseRedirect("/projectload/%s" % query.idtask)
	
@login_required
def deletefile(request):
	gethosts(request.session['host'] )
	users = getusers(request.session['name'])
	query = Task.objects.get(taskname=request.session['task'])
	param_a = request.POST['location']
	param_b = request.POST['namafile']
	basepathstatus = request.POST['basedir']
	command = "delfile"
	if(basepathstatus == "optiondefault"):
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = gethost.basepath, localbasepath = '', isdefault = 1)
	elif(basepathstatus == "optioncustom"):	
		basepath = request.POST['inputbasedir']
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = basepath, localbasepath = '', isdefault = 0)
	else:
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = '', localbasepath = '', isdefault = 0)
	addcommand.save()
	return HttpResponseRedirect("/projectload/%s" % query.idtask)
@login_required
def makedir(request):
	gethosts(request.session['host'] )
	users = getusers(request.session['name'])
	query = Task.objects.get(taskname=request.session['task'])
	param_a = request.POST['location']
	param_b = request.POST['namadir']
	basepathstatus = request.POST['basedir']
	command = "mkdir"
	if(basepathstatus == "optiondefault"):
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = gethost.basepath, localbasepath = '', isdefault = 1)
	elif(basepathstatus == "optioncustom"):	
		basepath = request.POST['inputbasedir']
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = basepath, localbasepath = '', isdefault = 0)
	else:
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = '', localbasepath = '', isdefault = 0)
	addcommand.save()
	return HttpResponseRedirect("/projectload/%s" % query.idtask)
@login_required
def uploadfile(request):
	gethosts(request.session['host'] )
	users = getusers(request.session['name'])
	query = Task.objects.get(taskname=request.session['task'])
	param_a = request.POST['destination']
	param_b = request.POST['namadokumen']
	param_c = request.POST['localbasepath']
	basepathstatus = request.POST['basedir']
	command = "uploadfile"
	if(basepathstatus == "optiondefault"):
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = gethost.basepath, localbasepath = param_c, isdefault = 1)
	elif(basepathstatus == "optioncustom"):	
		basepath = request.POST['inputbasedir']
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = basepath, localbasepath = param_c, isdefault = 0)
	else:
		addcommand = Commands(idtasks = query , commandname = command, parameter1 = param_a, parameter2 = param_b, hostetes = users.host, basespaths = '', localbasepath = param_c, isdefault = 0)
	addcommand.save()
	return HttpResponseRedirect("/projectload/%s" % query.idtask)
#--------------------------------------------------------------------------

#ini block script generator------------------------------------------------
@login_required
def refreshscript(request):
	with open ('temp/'+request.session['name']+ '_execute.py', 'r') as file:
		lines = file.readlines()
	with open ('temp/'+request.session['name']+ '_execute.py', 'w') as file:
		file.writelines("from fabric.api import execute\nfrom fabfile import *\n\n\n")
	file.close()
@login_required
def initscript(request):
	createscript(request)
	refreshscript(request)
@login_required
def createscript(request):
	open('temp/'+request.session['name']+ '_execute.py', 'w')#terpakai
@login_required
def deletescript(request):
	os.remove ('temp/'+request.session['name']+ '_execute.py')
@login_required
def writetoscript(request):
	query = Task.objects.get(taskname=request.session['task'])
	id = query.idtask
	taskhost = query.hostes
	command = Commands.objects.filter(idtasks__idtask = id )
	gethosts(request.session['host'] )
	with open ('temp/'+request.session['name']+ '_execute.py', 'r') as file:
		preset = file.readlines()
		data = file.readlines()	
	for field in command:
		commandidtask = str(field.idtasks.idtask)
		if (field.isdefault == 1):
			preset = "execute (preset,'"+taskhost.hostname+"' , '"+taskhost.username+"' , '"+taskhost.passwd+"' , '"+taskhost.basepath+"' , '"+field.localbasepath+"')"
			data = "execute ("+field.commandname+", '"+field.parameter1+"' , '"+field.parameter2+"' , '"+request.session['name']+"' , '"+commandidtask+"')"
		else:
			preset = "execute (preset,'"+taskhost.hostname+"' , '"+taskhost.username+"' , '"+taskhost.passwd+"' , '"+field.basespaths+"' , '"+field.localbasepath+"')"
			data = "execute ("+field.commandname+", '"+field.parameter1+"' , '"+field.parameter2+"' , '"+request.session['name']+"' , '"+commandidtask+"')"
		with open ('temp/'+request.session['name']+ '_execute.py', 'a') as file:
			writes = preset+"\n"+data+"\n"
			file.writelines(writes)
	file.close()
#backup script generator-----------------
#backup for revert---------------
@login_required
def initbackupscript(request):
	createbackupscript(request)
	refreshbackupscript(request)
@login_required
def refreshbackupscript(request):
	with open ('temp/'+request.session['name']+ '_backup.py', 'r') as file:
		lines = file.readlines()
	with open ('temp/'+request.session['name']+ '_backup.py', 'w') as file:
		file.writelines("from fabric.api import execute\nfrom fabfile import *\n\n\n")
	file.close()
@login_required
def createbackupscript(request):
	open('temp/'+request.session['name']+'_backup.py','w')
@login_required
def writebackupscript(request):
	query = Task.objects.get(taskname=request.session['task'])
	id = query.idtask
	taskhost = query.hostes
	command = Commands.objects.filter(idtasks__idtask = id)
	gethosts(request.session['host'] )
	with open ('temp/'+request.session['name']+'_backup.py','r') as file:
		preset = file.readlines()
		data = file.readlines()
	for field in command:
		commandidtask = str(field.idtasks.idtask)
		if (field.isdefault == 1):
			preset = "execute (preset,'"+taskhost.hostname+"' , '"+taskhost.username+"' , '"+taskhost.passwd+"' , '"+taskhost.basepath+"' , '"+field.localbasepath+"')"
			data = "execute (createbackup, '"+field.parameter1+"' , '"+field.parameter2+"' , '"+commandidtask+"' , '"+taskhost.basepath+"')"
		else:
			preset = "execute (preset,'"+taskhost.hostname+"' , '"+taskhost.username+"' , '"+taskhost.passwd+"' , '"+field.basespaths+"' , '"+field.localbasepath+"')"
			data = "execute (createbackup, '"+field.parameter1+"' , '"+field.parameter2+"' , '"+commandidtask+"' , '"+taskhost.basepath+"')"
		with open ('temp/'+request.session['name']+ '_backup.py', 'a') as file:
			writes = preset+"\n"+data+"\n"
			file.writelines(writes)
	file.close()
@login_required
def refreshbackupscript(request):
	with open ('temp/'+request.session['name']+ '_backup.py', 'r') as file:
		lines = file.readlines()
	with open ('temp/'+request.session['name']+ '_backup.py', 'w') as file:
		file.writelines("from fabric.api import execute\nfrom fabfile import *\n\n\n")
	file.close()
@login_required
def deletebackupscript(request):
	os.remove ('temp/'+request.session['name']+ '_backup.py')
#------------------------
#backup for rollback
@login_required
def inittempbackupscript(request):
	createtempbackupscript(request)
	refreshtempbackupscript(request)
@login_required
def refreshtempbackupscript(request):
	with open ('temp/'+request.session['name']+ '_tempbackup.py', 'r') as file:
		lines = file.readlines()
	with open ('temp/'+request.session['name']+ '_tempbackup.py', 'w') as file:
		file.writelines("from fabric.api import execute\nfrom fabfile import *\n\n\n")
	file.close()
@login_required
def createtempbackupscript(request):
	open('temp/'+request.session['name']+'_tempbackup.py','w')
@login_required
def writetempbackupscript(request):
	query = Task.objects.get(taskname=request.session['task'])
	id = query.idtask
	taskhost = query.hostes
	command = Commands.objects.filter(idtasks__idtask = id)
	gethosts(request.session['host'] )
	with open ('temp/'+request.session['name']+'_tempbackup.py','r') as file:
		preset = file.readlines()
		data = file.readlines()
	for field in command:
		commandidtask = str(field.idtasks.idtask)
		if (field.isdefault == 1):
			preset = "execute (preset,'"+taskhost.hostname+"' , '"+taskhost.username+"' , '"+taskhost.passwd+"' , '"+taskhost.basepath+"' , '"+field.localbasepath+"')"
			data = "execute (createtempexecbackup, '"+field.parameter1+"' , '"+field.parameter2+"' , '"+commandidtask+"' , '"+taskhost.basepath+"')"
		else:
			preset = "execute (preset,'"+taskhost.hostname+"' , '"+taskhost.username+"' , '"+taskhost.passwd+"' , '"+field.basespaths+"' , '"+field.localbasepath+"')"
			data = "execute (createtempexecbackup, '"+field.parameter1+"' , '"+field.parameter2+"' , '"+commandidtask+"' , '"+taskhost.basepath+"')"
		with open ('temp/'+request.session['name']+ '_tempbackup.py', 'a') as file:
			writes = preset+"\n"+data+"\n"
			file.writelines(writes)
	file.close()
@login_required
def refreshtempbackupscript(request):
	with open ('temp/'+request.session['name']+ '_tempbackup.py', 'r') as file:
		lines = file.readlines()
	with open ('temp/'+request.session['name']+ '_tempbackup.py', 'w') as file:
		file.writelines("from fabric.api import execute\nfrom fabfile import *\n\n\n")
	file.close()
@login_required
def deletetempbackupscript(request):
	os.remove ('temp/'+request.session['name']+ '_tempbackup.py')
#----------------------------------
#script rollback & revert generator------------------
#revert----------------------
@login_required
def initrevertscript(request):
	createrevertscript(request)
	refreshrevertscript(request)
@login_required
def refreshrevertscript(request):
	with open ('temp/'+request.session['name']+ '_revert.py', 'r') as file:
		lines = file.readlines()
	with open ('temp/'+request.session['name']+ '_revert.py', 'w') as file:
		file.writelines("from fabric.api import execute\nfrom fabfile import *\n\n\n")
	file.close()
@login_required
def createrevertscript(request):
	open('temp/'+request.session['name']+'_revert.py','w')
@login_required
def writerevertscript(request):
	query = Task.objects.get(idtask=request.session['idtask'])
	id = query.idtask
	taskhost = query.hostes
	command = Commands.objects.filter(idtasks__idtask = id)
	gethosts(request.session['host'] )
	with open ('temp/'+request.session['name']+'_revert.py','r') as file:
		preset = file.readlines()
		data = file.readlines()
	for field in command:
		commandidtask = str(field.idtasks.idtask)
		if (field.isdefault == 1):
			preset = "execute (preset,'"+taskhost.hostname+"' , '"+taskhost.username+"' , '"+taskhost.passwd+"' , '"+taskhost.basepath+"' , '"+field.localbasepath+"')"
			data = "execute (dorevert, '"+field.parameter1+"' , '"+field.parameter2+"' , '"+commandidtask+"' , '"+taskhost.basepath+"')"
		else:
			preset = "execute (preset,'"+taskhost.hostname+"' , '"+taskhost.username+"' , '"+taskhost.passwd+"' , '"+field.basespaths+"' , '"+field.localbasepath+"')"
			data = "execute (dorevert, '"+field.parameter1+"' , '"+field.parameter2+"' , '"+commandidtask+"' , '"+taskhost.basepath+"')"
		with open ('temp/'+request.session['name']+ '_revert.py', 'a') as file:
			writes = preset+"\n"+data+"\n"
			file.writelines(writes)
	file.close()
@login_required
def refreshrevertscript(request):
	with open ('temp/'+request.session['name']+ '_revert.py', 'r') as file:
		lines = file.readlines()
	with open ('temp/'+request.session['name']+ '_revert.py', 'w') as file:
		file.writelines("from fabric.api import execute\nfrom fabfile import *\n\n\n")
	file.close()
@login_required
def deleterevertscript(request):
	os.remove ('temp/'+request.session['name']+ '_revert.py')
#rollback if exec failed-------------------
@login_required
def initrollbackscript(request):
	createrollbackscript(request)
	refreshrollbackscript(request)
@login_required
def refreshrollbackscript(request):
	with open ('temp/'+request.session['name']+ '_rollback.py', 'r') as file:
		lines = file.readlines()
	with open ('temp/'+request.session['name']+ '_rollback.py', 'w') as file:
		file.writelines("from fabric.api import execute\nfrom fabfile import *\n\n\n")
	file.close()
@login_required
def createrollbackscript(request):
	open('temp/'+request.session['name']+'_rollback.py','w')
@login_required
def writerollbackscript(request):
	query = Task.objects.get(taskname=request.session['task'])
	id = query.idtask
	taskhost = query.hostes
	command = Commands.objects.filter(idtasks__idtask = id)
	gethosts(request.session['host'] )
	with open ('temp/'+request.session['name']+'_rollback.py','r') as file:
		preset = file.readlines()
		data = file.readlines()
	for field in command:
		commandidtask = str(field.idtasks.idtask)
		if (field.isdefault == 1):
			preset = "execute (preset,'"+taskhost.hostname+"' , '"+taskhost.username+"' , '"+taskhost.passwd+"' , '"+taskhost.basepath+"' , '"+field.localbasepath+"')"
			data = "execute (dorollbackexecutefail, '"+field.parameter1+"' , '"+field.parameter2+"' , '"+commandidtask+"' , '"+taskhost.basepath+"')"
		else:
			preset = "execute (preset,'"+taskhost.hostname+"' , '"+taskhost.username+"' , '"+taskhost.passwd+"' , '"+field.basespaths+"' , '"+field.localbasepath+"')"
			data = "execute (dorollbackexecutefail, '"+field.parameter1+"' , '"+field.parameter2+"' , '"+commandidtask+"' , '"+taskhost.basepath+"')"
		with open ('temp/'+request.session['name']+ '_rollback.py', 'a') as file:
			writes = preset+"\n"+data+"\n"
			file.writelines(writes)
	file.close()
@login_required
def refreshrollbackscript(request):
	with open ('temp/'+request.session['name']+ '_rollback.py', 'r') as file:
		lines = file.readlines()
	with open ('temp/'+request.session['name']+ '_rollback.py', 'w') as file:
		file.writelines("from fabric.api import execute\nfrom fabfile import *\n\n\n")
	file.close()
@login_required
def deleterollbackscript(request):
	os.remove ('temp/'+request.session['name']+ '_rollback.py')

#-------------------------------------------------------------------------
@login_required
def executetask(request):
	try:
		query = Task.objects.get(taskname=request.session['task'])
		writetoscript(request)
		writetempbackupscript(request)
		writerollbackscript(request)
		#backup to temp pertask
		writebackupscript(request)
		execfile('temp/'+request.session['name']+ '_backup.py')
		execfile('temp/'+request.session['name']+ '_tempbackup.py')
		execfile('temp/'+request.session['name']+ '_execute.py')
		refreshscript(request)
		refreshtempbackupscript(request)
		refreshrollbackscript(request)
		refreshbackupscript(request)
		
	except Exception as e:
		execfile('temp/'+request.session['name']+ '_rollback.py')
		refreshrollbackscript(request)
		refreshscript(request)
		refreshtempbackupscript(request)
		backs = request.META.get('HTTP_REFERER' )
		return TemplateResponse(request, "projectcek.html", {'error' : e.message, 'back' : backs })
	else:
		query.status = 1
		query.save()
	return HttpResponseRedirect("/tasklist/")
def reverttask(request, idtask):
	request.session['idtask'] = idtask
	writerevertscript(request)
	execfile('temp/'+request.session['name']+ '_revert.py')
	refreshrevertscript(request)
	return HttpResponseRedirect("/tasklist/")
	
	
