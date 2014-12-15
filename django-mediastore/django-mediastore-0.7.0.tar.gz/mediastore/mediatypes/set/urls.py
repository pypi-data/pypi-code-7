# -*- coding: utf-8 -*-
from django.conf.urls import *


urlpatterns = patterns('mediastore.mediatypes.set.views',
    url(r'^$', 'set_list', name='mediastore-set-list'),
    url(r'^(?P<set_slug>[^/]+)/$', 'set_detail', name='mediastore-set-detail'),
    url(r'^(?P<set_slug>[^/]+)/detail/(?P<slug>[^/]+)$', 'media_detail', name='mediastore-set-media-detail'),
)
