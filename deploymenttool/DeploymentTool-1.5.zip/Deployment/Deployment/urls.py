from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Deployment.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^$', 'Deploymentapp.views.home', name = 'home'),
	url(r'^login', 'Deploymentapp.views.signin', name = 'signin'),
	url(r'^tasklist/$', 'Deploymentapp.views.tasklist', name = 'task'),
	url(r'^projectload/(?P<idtask>[-\w]+)$','Deploymentapp.views.loadtask', name = 'tasklist'),	
	url(r'^deletetask/(?P<idtask>[-\w]+)$','Deploymentapp.views.deletetask', name = 'delete'),	
	url(r'^addnewtask/$', 'Deploymentapp.views.addnewtask', name = 'addnew'),
	url(r'^projecttask/$', 'Deploymentapp.views.addproject', name = 'projecttask'),
	url(r'^authentication/$', 'Deploymentapp.views.authentication', name = 'authentic'),
	url(r'^search/$', 'Deploymentapp.views.searchtask', name = 'search'),
	url(r'^changehostuser/$', 'Deploymentapp.views.changehostuser', name = 'chnghostusr'),
	url(r'^changehosttask/$', 'Deploymentapp.views.changehosttask', name = 'chnghosttask'),
	url(r'^loggedout/$', 'Deploymentapp.views.loggedout', name = 'loggedout'),
	url(r'^deletecommand/(?P<idcommand>[-\w]+)$','Deploymentapp.views.deletecommand', name = 'deletecommand'),
	url(r'^editcommand/(?P<idcommand>[-\w]+)$','Deploymentapp.views.runedit', name = 'editcommand'),
	url(r'^successedit/$', 'Deploymentapp.views.editcommand', name = 'edited'),
	url(r'^dorevert/(?P<idtask>[-\w]+)$', 'Deploymentapp.views.reverttask', name = 'reverttask'),	
#baru
	url(r'^copy/', 'Deploymentapp.views.copy', name='copy'),
	url(r'^newfile/', 'Deploymentapp.views.createfile', name='newfile'),
	url(r'^deletedirectory/', 'Deploymentapp.views.deletedir', name='deletedirectory'),
	url(r'^deletefile/', 'Deploymentapp.views.deletefile', name='deletefile'),
	url(r'^createdirectory/', 'Deploymentapp.views.makedir', name='createdirectory'),
	url(r'^uploadfile/', 'Deploymentapp.views.uploadfile', name='uploadfile'),
	url(r'^executetask/', 'Deploymentapp.views.executetask', name='executetask'),
	url(r'^deleteallcommand/','Deploymentapp.views.deleteallcommand', name = 'deleteallcommand'),
)
handler404 = "Deploymentapp.views.error404"