import csv
import datetime
import decimal
import re

from django.conf.urls import patterns
from django.contrib import admin
from django.contrib.admin.util import lookup_field, label_for_field
from django.http import HttpResponse
from django.utils import formats, timezone, six
from django.utils.encoding import smart_text
from django.utils.html import strip_tags


# based on admin.util.display_for_value
def display_for_value(value, boolean=False):
    if value is None:
        return ''
    if isinstance(value, bool):
        if value == True:
            return 'X'
        return ''
    elif isinstance(value, datetime.datetime):
        return formats.localize(timezone.template_localtime(value))
    elif isinstance(value, (datetime.date, datetime.time)):
        return formats.localize(value)
    elif isinstance(value, six.integer_types + (decimal.Decimal, float)):
        return formats.number_format(value)
    else:
        return perform_substitutions(smart_text(value))

def perform_substitutions(value):
    value = value.replace('&nbsp;', ' ')
    return strip_tags(re.sub('<br ?/?>', '\n', value))

def csv_value(field_name, obj, modeladmin):
    f, attr, value = lookup_field(field_name, obj, modeladmin)
    return unicode(display_for_value(value)).encode('utf-8', 'replace')

def csv_header(modeladmin, field_name):
    return label_for_field(field_name, modeladmin.model, modeladmin, False).title()

def csv_file_name(opts):
    return '%s_%s.csv' % (opts.verbose_name_plural.title().replace('.', '_'), datetime.date.today())

def export_as_csv(modeladmin, queryset):
    opts = modeladmin.model._meta

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % csv_file_name(opts)
    writer = csv.writer(response)

    fields = [field for field in modeladmin.list_display if field not in modeladmin.hide_from_export]

    writer.writerow([csv_header(modeladmin, field_name) for field_name in fields])
    for obj in queryset:
        writer.writerow([csv_value(field_name, obj, modeladmin) for field_name in fields])
    return response

class ExportModelAdmin(admin.ModelAdmin):
    change_list_template = 'admin/exporter_change_list.html'
    hide_from_export = ()

    def get_urls(self):
        urls = super(ExportModelAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^export/$', self.export_view),
        )
        return my_urls + urls

    def export_view(self, request):
        # instantiate a ChangeList so we can jack its query set
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        list_filter = self.get_list_filter(request)

        ChangeList = self.get_changelist(request)
        cl = ChangeList(request, self.model, list_display,
            list_display_links, list_filter, self.date_hierarchy,
            self.search_fields, self.list_select_related,
            self.list_per_page, self.list_max_show_all, self.list_editable,
            self)

        return export_as_csv(self, cl.get_query_set(request))
