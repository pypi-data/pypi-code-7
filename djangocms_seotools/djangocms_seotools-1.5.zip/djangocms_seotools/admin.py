# -*- coding: utf-8 -*-

__author__ = "Nikolay Dolganov"
__email__ = "SirNikolasd@yandex.ru"


# *********************************
# Page Titles
# *********************************

from django.contrib import admin
from cms.extensions import PageExtensionAdmin

from .models import Metadata


class TitlesAndMetaAdmin(PageExtensionAdmin):
    pass

admin.site.register(Metadata, TitlesAndMetaAdmin)