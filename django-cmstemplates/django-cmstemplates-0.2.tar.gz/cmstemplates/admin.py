# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from cmstemplates.models import Template, TemplateGroup

USE_CODEMIRROR = getattr(settings, 'CMSTEMPLATES_USE_CODEMIRROR', False)


class TemplateAdminForm(forms.ModelForm):
    """Form which validates template saving process."""
    model = Template

    def __init__(self, *args, **kwargs):
        super(TemplateAdminForm, self).__init__(*args, **kwargs)

        if USE_CODEMIRROR:
            from codemirror import CodeMirrorTextarea

            self.fields['content'].widget = CodeMirrorTextarea(
                mode='htmlmixed',
                dependencies=('javascript', 'xml', 'css')
            )


class TemplateGroupAdmin(admin.ModelAdmin):
    # TODO: add templates count
    list_display = ['name']


class TemplateAdmin(admin.ModelAdmin):
    list_display = [
        '__unicode__', 'group', 'weight', 'is_active',
    ]
    list_editable = ['weight', 'is_active']
    list_filter = ['group__name']
    save_on_top = True
    search_fields = ['id', 'group__name', 'weight', 'content']
    form = TemplateAdminForm


admin.site.register(TemplateGroup, TemplateGroupAdmin)
admin.site.register(Template, TemplateAdmin)
