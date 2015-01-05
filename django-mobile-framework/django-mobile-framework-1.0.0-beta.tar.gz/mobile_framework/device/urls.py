from django.conf.urls import patterns, url

from mobile_framework.device.views import CreateDevice, RetrieveUpdateDevice 

urlpatterns = patterns('',
    url(r'^$', CreateDevice.as_view()),
    url(r'^(?P<pk>.+)/$', RetrieveUpdateDevice.as_view())
)
