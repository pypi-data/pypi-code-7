# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import SmartProxyRequest, SmartProxyRequestParameter, SmartProxyResponse


class SmartProxyResponseInline(admin.StackedInline):
    model = SmartProxyResponse


class SmartProxyRequestParameterInline(admin.TabularInline):
    model = SmartProxyRequestParameter
    extra = 1


class SmartProxyRequestAdmin(admin.ModelAdmin):
    list_display = ('method', 'domain', 'port', 'path', 'querystring_display', 'date')
    list_filter = ('method', 'domain', 'port')
    inlines = (SmartProxyRequestParameterInline, SmartProxyResponseInline)


class SmartProxyResponseAdmin(admin.ModelAdmin):
    list_display = ('request_domain', 'request_path', 'request_querystring', 'status', 'content_type')
    list_filter = ('status', 'content_type')


admin.site.register(SmartProxyRequest, SmartProxyRequestAdmin)
admin.site.register(SmartProxyResponse, SmartProxyResponseAdmin)
