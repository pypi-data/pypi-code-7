# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from cmstemplates.models import TemplateZone, TemplateFile

USE_CODEMIRROR = getattr(settings, 'ZONE_TEMPLATE_USE_CODEMIRROR', False)


class TemplateFileAdminForm(forms.ModelForm):
    """Form which validates template file saving process."""
    model = TemplateFile

    def __init__(self, *args, **kwargs):
        super(TemplateFileAdminForm, self).__init__(*args, **kwargs)

        if USE_CODEMIRROR:
            from codemirror import CodeMirrorTextarea

            self.fields['template_content'].widget = CodeMirrorTextarea(
                mode='htmlmixed',
                dependencies=('javascript', 'xml', 'css')
            )

    def clean(self):
        """Validate user input."""
        cleaned_data = super(TemplateFileAdminForm, self).clean()

        template_filename = cleaned_data.get('template_filename')
        use_content = cleaned_data.get('use_content')
        template_content = cleaned_data.get('template_content')

        if use_content:
            if not template_content:
                # u'Невозможно использовать пустой текст шаблона'
                raise forms.ValidationError(
                    _('Template content must not be empty'))
        else:
            if not template_filename:
                # u'Укажите имя файла шаблона'
                raise forms.ValidationError(
                    _('Please, provide template file name'))

        return cleaned_data


class TemplateZoneAdmin(admin.ModelAdmin):
    list_display = ['name']


class TemplateFileAdmin(admin.ModelAdmin):
    list_display = [
        '__unicode__', 'source_path', 'zone',
        'weight', 'is_active',
    ]
    list_editable = ['weight', 'is_active']
    list_filter = ['zone__name', 'use_content']
    save_on_top = True
    search_fields = [
        'id', 'zone__name', 'weight',
        'template_filename', 'template_content'
    ]
    form = TemplateFileAdminForm


admin.site.register(TemplateZone, TemplateZoneAdmin)
admin.site.register(TemplateFile, TemplateFileAdmin)
