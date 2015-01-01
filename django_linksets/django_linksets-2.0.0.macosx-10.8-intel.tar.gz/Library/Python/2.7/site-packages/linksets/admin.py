from django.contrib import admin
from django.db import models

from .models import LinkItem


class LinkItemInlines(admin.StackedInline):
    model = LinkItem
    fk_name = "parent"
    verbose_name = "Child Link"
    verbose_name_plural = "Child Links"

    extra = 0

    fieldsets = (
        ("", {
            'fields': (
                ('order', 'display_name', 'url', ),
            )
        }),
    )
    ordering = ('order',)


class LinkItemAdmin(admin.ModelAdmin):

    fieldsets = (
        ('Link Items', {'fields': ('parent', 'display_name', 'txtid',
         ('hide'),
         'url')}),
    )

    list_display = ('admin_title', 'display_name',)
    list_display_links = ('display_name',)
    list_filter = ('parent',)
    readonly_fields = ('txtid',)

    autocomplete_lookup_fields = {
        'fk': ['parent']
    }
    raw_id_fields = ('parent',)
    inlines = [LinkItemInlines]
    ordering = ('path',)

    def reindex_items(self, request, queryset):
        for item in queryset:
            LinkItemIndex().update_object(item)
        messages.success(request, '%s items reindexed.' % (len(queryset)))

    def lookup_allowed(self, key, value):
        """Enable Admin Filtering by Parent TextID"""
        if key in ('parent__txtid',):
            return True

        return super(LinkItemAdmin, self).lookup_allowed(key, value)


admin.site.register(LinkItem, LinkItemAdmin)
