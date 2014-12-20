# coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from .models import SESStat


class SESStatAdmin(admin.ModelAdmin):
    list_display = ('date', 'delivery_attempts', 'bounces', 'complaints',
                    'rejects')

admin.site.register(SESStat, SESStatAdmin)
