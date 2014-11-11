from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponseRedirect

urlpatterns = patterns(
    '',
    url(r'^$', lambda request: HttpResponseRedirect('/admin/')),
    url(r'^admin/', include(admin.site.urls)),
)
