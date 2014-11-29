from django.conf.urls import patterns, url
from .views import index

urlpatterns = patterns('',
	(r'^$', index),
	
	
)

