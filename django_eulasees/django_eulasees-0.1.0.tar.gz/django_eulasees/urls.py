from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from django_eulasees import api

urlpatterns = [
    url(r'^raweulas/$', api.RawEulaList.as_view()),
    url(r'^raweulas/(?P<pk>[0-9]+)/$', api.RawEulaList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
