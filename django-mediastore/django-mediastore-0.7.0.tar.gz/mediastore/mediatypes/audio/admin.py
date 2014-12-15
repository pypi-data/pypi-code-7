from django import forms
from django.contrib import admin
from mediastore.admin import MediaAdmin
from mediastore.mediatypes.audio.models import Audio


class AudioAdmin(MediaAdmin):
    list_display = ('id', 'name', 'file_extension',  'created')
    list_filter = ('file_extension',)


admin.site.register(Audio, AudioAdmin)
