# -*- coding: utf-8 -*-
from django.contrib import admin
from mediastore.admin import MediaAdmin
from mediastore.mediatypes.embeded.models import Embeded


class EmbededAdmin(admin.ModelAdmin):
    pass


admin.site.register(Embeded, EmbededAdmin)

