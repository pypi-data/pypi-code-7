from django.conf.urls import patterns, include, url

from . import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^/$', views.get_proxy),
    url(r'^proxy/$', views.get_proxy, name="proxyurl"),
    url(r'^proxy/(?P<service_slug>[\w-]+)/$', views.get_proxy),
    url(r'^proxy/(?P<service_slug>[\w-]+)/(?P<resource_slug>[\w-]+)$', views.get_proxy),

    url(r'^maprender/$', views.maprender),
    url(r'^maprender/(?P<wsName>[\w-]+)/$', views.maprender),
    url(r'^maprender/(?P<wsName>[\w-]+)/(?P<viewId>[\w-]+)$', views.maprender),

    (r'^admin/', include(admin.site.urls)),
)
