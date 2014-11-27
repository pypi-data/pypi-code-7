# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'chunks.views',
    url(r'^edit/(?P<key>\w+)/$', 'edit_view', name='edit'),
)
