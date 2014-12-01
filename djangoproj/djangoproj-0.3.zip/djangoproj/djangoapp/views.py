from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from djangoapp.models import DjangoApp
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import io

#class submit
i = 3
from django.shortcuts import render_to_response
def handlerrequest(request):
	if request.method == 'POST':
		nama = request.POST['nameTxt']
		the_value = {'the_name' : nama}
		render_to_response('hasil_post.html')
		#render_to_response('hasil_post.html', path)
	return render_to_response ('hasil_post.html', the_value)
		#message = request.POST['nameTxt']
	#else:
		#message = 'You submitted an empty form.'
	#return HttpResponse(message)
# Create your views here.
def home(request):
	return TemplateResponse (request, "home.html", {'apps' : DjangoApp.objects.all()})
def command(request, slug):
	commands = get_object_or_404(DjangoApp, slug=slug)
	return TemplateResponse(request, "command.html", {'app' : commands})
def form(request):
	return TemplateResponse (request, "form.html")
def urlbad(request):
	return HttpResponse ("Welcome to the page at /current/")
def urlgood(request):
	return HttpResponse ("Welcome to the page at %s" % request.path)
def uabad(request):
	ua = request.META['HTTP_USER_AGENT']  # Might raise KeyError!
	return HttpResponse("Your browser is %s" % ua)
def uagood(request):
    ua = request.META.get('HTTP_USER_AGENT', 'unknown')
    return HttpResponse("Your browser is %s" % ua)
def search_form(request):
	return render(request, 'search_form.html')
def search(request):
	if 'q' in request.GET:
		message = 'You searched for: %r' % request.GET['q']
	else:
		message = 'You submitted an empty form.'
		
#INI YANG BARU--------------------------------------------------------------------
#copy
def copyform(request):
	return TemplateResponse (request, "copy.html")
def copy(request):
	if request.method == 'POST':
		param_a = request.POST['location']
		param_b = request.POST['destination']
		if (param_a != '') and (param_b != ''):
			with open('djangoapp/execute.py', 'r') as file:
				data = file.readlines()
			data[i] = ("execute (copy, '"+param_a+"', '"+param_b+"')\n ")
			with open('djangoapp/execute.py', 'w') as file:
				file.writelines(data)
			file.close()
			return TemplateResponse (request,"execute.html")
		else:
			return HttpResponse ("masukkan inputannya!!")
#add
def add(request):
	global i
	i = i + 1
	return TemplateResponse (request, "home.html")

#makedir
def makedirform(request):
	return TemplateResponse (request, "makedir.html")
def makedir(request):
	if request.method == 'POST':
		param_a = request.POST['namadir']
		if(param_a != ''):
			with open('djangoapp/execute.py', 'r') as file:
				data = file.readlines()
			data[i] = ("execute (mkdir, '"+param_a+"')\n ")
			with open('djangoapp/execute.py', 'w') as file:
				file.writelines(data)
			file.close()
			return TemplateResponse (request,"execute.html")
		else:
			return HttpResponse ("masukkan inputannya!!")

#remove empty directory
def removdirform(request):
	return TemplateResponse (request, "removedir.html")
def removdir(request):
	if request.method == 'POST':
		param_a = request.POST['namadir']
		if(param_a != ''):
			with open('djangoapp/execute.py', 'r') as file:
				data = file.readlines()
			data[i] = ("execute (rmdir, '"+param_a+"')\n ")
			with open('djangoapp/execute.py', 'w') as file:
				file.writelines(data)
			file.close()
			return TemplateResponse (request, "execute.html")
		else:
			return HttpResponse ("masukkan inputannya!!")

#remove entire directory
def deletedirform(request):
	return TemplateResponse (request, "deletedir.html")
def deletedir(request):
	if request.method == 'POST':
		param_a = request.POST['namadir']
		if(param_a != ''):
			with open('djangoapp/execute.py', 'r') as file:
				data = file.readlines()
			data[i] = ("execute (deldir, '"+param_a+"')\n ")
			with open('djangoapp/execute.py', 'w') as file:
				file.writelines(data)
			file.close()
			return TemplateResponse (request, "execute.html")
		else:
			return HttpResponse ("masukkan inputannya!!")

#Create a file
def createfileform(request):
	return TemplateResponse (request, "createfile.html")
def createfile(request):
	if request.method == 'POST':
		param_a = request.POST['namafile']
		if(param_a != ''):
			with open('djangoapp/execute.py', 'r') as file:
				data = file.readlines()
			data[i] = ("execute (touchfile, '"+param_a+"')\n ")
			with open('djangoapp/execute.py', 'w') as file:
				file.writelines(data)
			file.close()
			return TemplateResponse (request, "execute.html")
		else:
			return HttpResponse ("masukkan inputannya!!")

#Delete a file
def deletefileform(request):
	return TemplateResponse(request, "deletefile.html")
def deletefile(request):
	if request.method == "POST":
		param_a =  request.POST['namafile']
		if(param_a != ''):
			with open('djangoapp/execute.py', 'r') as file:
				data = file.readlines()
			data[i] = ("execute (removefile, '"+param_a+"')\n ")
			with open('djangoapp/execute.py', 'w') as file:
				file.writelines(data)
			file.close()
			return TemplateResponse (request, "execute.html")
		else:
			return HttpResponse ("masukkan inputannya!!")

#executor	
def refresh():
	global i
	i = 3
def refreshscript():
	refresh()
	global i
	with open ('djangoapp/execute.py', 'r') as file:
		lines = file.readlines()
	lines[i] = ''
	with open ('djangoapp/execute.py', 'w') as file:
		while(i > 3):
			file.writelines(lines)
			i = i-1
		file.writelines('from fabric.api import execute\nfrom fabfile import *\n\n\n')
	file.close()
def execpy(request):
	execfile('djangoapp/execute.py')
	refreshscript()
	return HttpResponse ("perintah berhasil dilaksanakan")
		
	
	
#	return HttpResponse(message)
#def rmdir(request)
#	execute(
	