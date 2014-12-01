from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	#yang lama
	url(r'^djangoapp/(?P<slug>[-\w]+)/$', 'djangoapp.views.command', name = 'app'),
    #latihan get post
	url(r'^form/process/$', 'djangoapp.views.handlerrequest', name='hasil_post'),
	url(r'^form/$', 'djangoapp.views.form', name = 'form'),
	#url(r'^makedir/$', 'djangoapp.views.mkdir', name = 'makedir'),
	#url(r'^list/$', 'djangoapp.views.list', name = 'list'),
    url(r'^contact/', 'form.views.contact', name='contact'),
	url(r'^search-form/$', 'djangoapp.views.search_form', name='search_form'),
	#url tes tes
	url(r'^uagood/', 'djangoapp.views.uagood', name='uagood'),
	url(r'^uabad/', 'djangoapp.views.uabad', name='uabad'),

	
	# yang baru
	url(r'^admin/', include(admin.site.urls)),
	url(r'^$', 'djangoapp.views.home', name='home'),
	#copy file
	url(r'^copy-form/', 'djangoapp.views.copyform', name='copyform'),
	url(r'^copy/', 'djangoapp.views.copy', name= 'copy'),
	#executor
	url(r'^execute/', 'djangoapp.views.execpy', name= 'execute'),
	#nambah add
	url(r'^add/', 'djangoapp.views.add', name = 'add'),
	#makedir
	url(r'^makedir-form/', 'djangoapp.views.makedirform', name='makedirform'),
	url(r'^makedir/', 'djangoapp.views.makedir', name='makedir'),
	#removedir
	url(r'^removdir-form/', 'djangoapp.views.removdirform', name='removdirform'),
	url(r'^removdir/', 'djangoapp.views.removdir', name='removdir'),
	#deletedir
	url(r'^deletedir-form/','djangoapp.views.deletedirform', name='deletedirform'),
	url(r'^deletedir/', 'djangoapp.views.deletedir', name='deletedir'),
	#createfile
	url(r'^createfile-form/', 'djangoapp.views.createfileform', name='createfileform'),
	url(r'^createfile/', 'djangoapp.views.createfile', name='createfile'),
	#deletefile
	url(r'^deletefile-form/', 'djangoapp.views.deletefileform', name='deletefileform'),
	url(r'^deletefile/', 'djangoapp.views.deletefile', name='deletefile'),
	
	#tes
	url(r'^link-to-fun1$', views.fun1),
)