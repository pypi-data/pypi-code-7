# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from mediastore.admin import MediaAdmin
from mediastore.mediatypes.video.models import Video, QueueItem


class QueueItemInline(admin.StackedInline):
    model = QueueItem
    extra = 0


class VideoAdmin(MediaAdmin):
    list_display = ('id', 'preview', 'name', 'is_ready', 'errors', 'created')
    fieldsets = (
        MediaAdmin.MAIN_FIELDSET,
        (_('Data'), {
            'fields': ('file', 'thumbnail',)
        })
    )
    list_filter = ('is_ready',)
    inlines = [QueueItemInline]

    def errors(self, obj):
        queryset = obj.queueitem_set.all()
        if queryset.count():
            return queryset.filter(error=True).count() != 0
        return False
    errors.boolean = True

admin.site.register(Video, VideoAdmin)
