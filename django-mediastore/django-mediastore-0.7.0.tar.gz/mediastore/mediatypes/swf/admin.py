# -*- coding: utf-8 -*-
from django.contrib import admin
from mediastore.admin import MediaAdmin
from mediastore.mediatypes.swf.models import SWF


class SWFAdmin(MediaAdmin):
    list_display = ('id', 'name', 'created')


admin.site.register(SWF, SWFAdmin)
