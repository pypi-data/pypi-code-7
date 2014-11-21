from models import *
from django.contrib import admin

class HashLinkAdmin(admin.ModelAdmin):
    list_display = ['content_type',
                    'object_id',
                    'content_object',
                    'user',
                    'allow_anonymous',
                    'expiration_datetime',
                    'creation_datetime',
                    'key', 'action']
    raw_id_fields = ("user",)

admin.site.register(HashLink, HashLinkAdmin)
