# -*- coding: utf-8 -*-
from django.contrib import admin
from mediastore.admin import MediaAdmin
from mediastore.mediatypes.set.models import Set


class SetAdmin(MediaAdmin):
    list_display = (
        'id',
        'preview',
        'name',
        'created')

admin.site.register(Set, SetAdmin)
