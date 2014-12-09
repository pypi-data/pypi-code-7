# encoding=utf-8

from django.forms import *


class BooleanField(Field):

    def validate(self, value):
        if value is None and self.required:
            raise ValidationError(self.error_messages['required'], code='required')

    def _has_changed(self, initial, data):
        return initial != data




