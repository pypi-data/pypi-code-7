# -*- coding: utf-8 -*-

__author__ = "Nikolay Dolganov"
__email__ = "SirNikolasd@yandex.ru"

"""
This URLs are used for the extension's tests.
Do not use it in production.
"""

from django.contrib import admin
from django.conf.urls import url, patterns, include

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('cms.urls')),
)