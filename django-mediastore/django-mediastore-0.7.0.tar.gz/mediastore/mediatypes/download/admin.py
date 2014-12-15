from django import forms
from django.contrib import admin
from mediastore.admin import MediaAdmin
from mediastore.mediatypes.download.models import Download


class DownloadAdmin(MediaAdmin):
    list_display = ('id', 'name', 'file_extension',  'file_size', 'created')
    list_filter = ('file_extension',)


admin.site.register(Download, DownloadAdmin)
