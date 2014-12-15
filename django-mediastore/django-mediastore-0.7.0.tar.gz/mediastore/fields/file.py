# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django import forms
from mediastore.utils.files import has_file_extension


class FileFormField(forms.FileField):
    default_error_messages = {
        'invalid': _(u"No file was submitted. Check the encoding type on the form."),
        'missing': _(u"No file was submitted."),
        'empty': _(u"The submitted file is empty."),
        'max_length': _(u'Ensure this filename has at most %(max)d characters (it has %(length)d).'),
        'wrong_extension': _(u'Ensure that you only upload %(extensions)s files.'),
        'validation_failed': _(u'Ensure that you upload a valid file.'),
    }

    def __init__(self, *args, **kwargs):
        self.allowed_extensions = kwargs.pop('allowed_extensions', None)
        self.validation_function = kwargs.pop('validation_function', None)
        super(FileFormField, self).__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        data = super(FileFormField, self).clean(data, initial)
        if self.allowed_extensions is not None:
            if not has_file_extension(data.name, self.allowed_extensions):
                raise forms.ValidationError(
                    self.error_messages['wrong_extension'] % {
                        'extensions': ', '.join(self.allowed_extensions)
                    })
        if self.validation_function:
            if not self.validation_function(data):
                raise forms.ValidationError(
                    self.error_messages['validation_failed'])
        return data


class FileField(models.FileField):
    def __init__(self, *args, **kwargs):
        self.allowed_extensions = kwargs.pop('allowed_extensions', None)
        self.validation_function = kwargs.pop('validation_function', None)
        super(FileField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': FileFormField,
            'allowed_extensions': self.allowed_extensions,
            'validation_function': self.validation_function,
        }
        defaults.update(kwargs)
        return super(FileField, self).formfield(**defaults)
