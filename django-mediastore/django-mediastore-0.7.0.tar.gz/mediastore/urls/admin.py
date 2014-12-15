from django.conf.urls.defaults import *
from mediastore import views


urlpatterns = patterns('',
    url(r'^mediastore/media/add/$', views.admin.add, name='admin-media-add'),
)
