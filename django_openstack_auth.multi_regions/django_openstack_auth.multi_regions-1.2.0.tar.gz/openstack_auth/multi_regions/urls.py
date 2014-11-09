# -*- coding: utf-8 -*-
# Copyright 2014 Powerleader, PLCLOUD
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>
from django.conf.urls import patterns
from django.conf.urls import url

from openstack_auth.urls import urlpatterns as auth_urlpatterns


urlpatterns = patterns(
    'openstack_auth.multi_regions.views',
    url(r"^login/$", "login", name='login'),
    url(r'^switch_region/(?P<region_name>[^/]+)/$', 'switch_region_external',
        name='switch_region_external'),
    url(r'^api/switch_region/$', 'api_switch_region',
        name='api_switch_region')
)

urlpatterns += auth_urlpatterns
