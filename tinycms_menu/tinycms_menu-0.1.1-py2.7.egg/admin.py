from django.contrib import admin

from models import *
from tinycms.admin import register


class MenuItemAdmin(admin.ModelAdmin):
    list_display  = ['page','language','title']
admin.site.register(MenuItem,MenuItemAdmin)


class MenuInline(admin.StackedInline):
    model = MenuItem
    extra = 1

register(MenuInline,0)


