# -*- coding: utf-8 -*-

from django.db.models.fields.files import ImageField
from django.contrib import admin

from . import models
from . import widgets


class ChunkAdmin(admin.ModelAdmin):
    list_display = ('key', 'content')
    search_fields = ('key', 'content')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('key', 'content')
    list_filter = ('key', )
    search_fields = ('key', 'content')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('key', )
    search_fields = ('key', )

    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, ImageField):
            kwargs['widget'] = widgets.CustomizedImageWidget
        return super(ImageAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)


class MediaAdmin(admin.ModelAdmin):
    list_display = ('key', 'title')
    search_fields = ('key', 'title', 'desc')


admin.site.register(models.Chunk, ChunkAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Image, ImageAdmin)
admin.site.register(models.Media, MediaAdmin)
