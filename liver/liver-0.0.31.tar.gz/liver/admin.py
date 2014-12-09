from models import *

import logging
logger = logging.getLogger("liver.admin")

from django import forms
from django.contrib import admin
from django.db.models import Q

from django.utils.translation import ugettext_lazy, ugettext as _

import datetime, time, pytz, calendar

def clone(modeladmin, request, queryset):
    for o in queryset:
        o.clone()
clone.short_description = _("Clone")

class RecordingRuleInLine(admin.TabularInline):
        model = RecordingRule
        extra = 1

class RecordingMetadataInLine(admin.TabularInline):
        model = RecordingMetadata
        extra = 1

class RecordingJobMetadataInLine(admin.TabularInline):
        model = RecordingJobMetadata
        extra = 1

class RecordingSourceAdmin(admin.ModelAdmin):
    actions = [
            clone,
    ]

    inlines = [
                RecordingRuleInLine,
                RecordingMetadataInLine,
    ]

    list_display = [
            'sources_group',
            # 'insertion_date',
            'modification_date',
            'enabled',
            'enabled_since',
            'enabled_until',
            'edit_html',
    ]

    list_editable = [
            'sources_group',
            'enabled',
            'enabled_since',
            'enabled_until',

    ]

    list_display_links = ['edit_html']

    list_per_page = 200

    def edit_html(self, queryset):
        return '''<a href="%s/">Edit</a>''' % queryset.id
    edit_html.short_description = ''
    edit_html.allow_tags = True



class RecordingJobAdmin(admin.ModelAdmin):
    ordering = ['-scheduled_start_date']

    actions = [
            "wait",
            "cancel",
            "success",
            "launch_now",
            clone,
    ]

    def launch_now(self, request, queryset):
        d = datetime.datetime.fromtimestamp(time.time(), pytz.UTC)
        queryset.update(status="waiting",scheduled_start_date=d)
    launch_now.short_description=_("Launch now")

    def wait(self, request, queryset):
        queryset.update(status="waiting")
    wait.short_description=_("Set to waiting")

    def cancel(self, request, queryset):
        queryset.update(status="cancelled")
    cancel.short_description=_("Set to cancelled")

    def success(self, request, queryset):
        queryset.update(status="successful")
    success.short_description=_("Set to successful")

    date_hierarchy = 'scheduled_start_date'

    list_per_page = 200

    search_fields = ['status','recordingjobmetadata__value' ]

    exclude = ["recording_source"]
    readonly_fields = [
            'insertion_date',
            'modification_date',
            'execution_date',
            'completion_date',
            'scheduled_end_date',
    ]

    fieldsets = (
        (None, {
            'fields': (
                (
            'sources_group',
            'scheduled_start_date',
            'scheduled_end_date',
            'scheduled_duration',
            'enabled',
                ),

            )
        }),
        (_("Process"), {
            'fields': (
                (
            'status',
            'recorder',
            'result',
                ),
                (
            'insertion_date',
            'modification_date',
            'execution_date',
            'completion_date',
                ),

            )
        }),

    )

    list_display = [
      'pretty_name',
      'scheduled_start_date',
      'scheduled_end_date',
      'scheduled_duration',
      'insertion_date',
      'modification_date',
      'execution_date',
      'status',
    ]

    list_filter = [
            "enabled",
            "status",
            "recording_source",
            "recorder",
    ]

    inlines = [
        RecordingJobMetadataInLine,
    ]

class RecordingAdmin(admin.ModelAdmin):
    search_fields = ['name', 'metadata_json', 'profiles_json']

    ordering = ['-insertion_date']

    actions = [
            # clone,
    ]

    readonly_fields = [
            'name',
            'insertion_date',
            'modification_date',
            'recording_job',
            'profiles',
            'metadata',
    ]

    fieldsets = (
        (None, {
            'fields': (
                (
            'name',
            'insertion_date',
            'modification_date',
                ),

            )
        }),
        (_("Information"), {
            'fields': (
                (
            'profiles',
            'metadata',
                ),
            )
        }),

    )


    list_display = [
            'name',
            'insertion_date',
            'modification_date',
            'profiles',
            'metadata',
    ]

    list_per_page = 200

    def has_add_permission(self, request):
        return False

    def queryset(self, request):
        qs = super(RecordingAdmin, self).queryset(request)
        return qs.filter(Q(to_delete=False))


class SourceInLine(admin.TabularInline):
    model = Source
    fk_name = 'sources_group'
    extra = 0

class SourcesGroupAdmin(admin.ModelAdmin):
    actions = [
            clone,
    ]
    ordering = ['name']

    readonly_fields = [
            'insertion_date',
            'modification_date',
    ]

    fieldsets = (
        (None, {
            'fields': (
                (
            'name',
            'external_id',
                ),

            )
        }),
        (None, {
            'fields': (
                (
            'insertion_date',
            'modification_date',
                ),

            )
        }),
        (None, {
            'fields': (
                (
            'default_offset_start',
            'default_offset_end',
            'default_availability_window',
                ),

            )
        }),
    )

    inlines = [
      SourceInLine,
    ]


class RecorderAdmin(admin.ModelAdmin):
    ordering = ['name','token']


class ApplicationAdmin(admin.ModelAdmin):

    readonly_fields = [
            'id',
            'sync_time',
    ]

    list_editable = ['name','token', 'valid', 'valid_since','valid_until']

    list_display_links = ['edit_html']
    list_display = ('name', 'token', 'description',
            'valid', 'valid_since', 'valid_until',
            'modification_time', "edit_html")
    # list_filter = ['valid', 'source_host','enabled',
    #         ]
    search_fields = ['name', 'description','token',
            ]
    date_hierarchy = 'insertion_time'
    list_per_page = 200

    fieldsets = [
            (None,{
              'fields': [
                ('name','token'),
                ('valid','valid_since', 'valid_until','sync_time'),
                (),
            ]}),
            ('Other info', {
              'classes': ('collapse',),
              'fields': (
                ("description"),
              )
            }),
    ]

    def edit_html(self, queryset):
        return '''<a href="%s/">Edit</a>''' % queryset.id
    edit_html.short_description = ''
    edit_html.allow_tags = True



# admin.site.register(Source)
admin.site.register(SourcesGroup,SourcesGroupAdmin)
admin.site.register(Recorder,RecorderAdmin)
admin.site.register(RecordingSource,RecordingSourceAdmin)
admin.site.register(RecordingJob,RecordingJobAdmin)
admin.site.register(Recording,RecordingAdmin)
admin.site.register(Application,ApplicationAdmin)

