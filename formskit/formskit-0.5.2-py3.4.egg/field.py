from json import dumps
from base64 import urlsafe_b64encode

from .messages import Message
from .field_convert import FakeConvert


class Field(object):

    def __init__(self,
                 name,
                 validators=None,
                 label=None,
                 ignore=False,
                 convert=FakeConvert()):
        self.name = name
        self.label = label
        self.ignore = ignore
        self.form = None
        self.init_validators(validators)
        self.init_convert(convert)
        self.reset()

    def init_validators(self, validators=None):
        self.validators = []
        validators = validators or []
        for validator in validators:
            validator.init_field(self)
            self.validators.append(validator)

    def init_form(self, form):
        self.form = form

    def init_convert(self, convert):
        self.convert = convert
        self.convert._set_field(convert)

    def reset(self):
        self.values = []
        self.messages = []
        self.error = False

    def validate(self):
        for validator in self.validators:
            validator.make_field()

        if self.error:
            return False

        for validator in self.validators:
            for value in self.values:
                validator.make_value(value)
        return not self.error

    def set_error(self, text):
        self.error = True
        message = Message()
        message.init(text, field=self)
        self.messages.append(message)

    def get_value(self, index=0, default=NotImplemented):
        try:
            field_value = self.values[index]
        except IndexError:
            if default is NotImplemented:
                raise
            else:
                return default
        return self.convert(field_value.value)

    def get_value_error(self, index=0, default=NotImplemented):
        try:
            field_value = self.values[index]
        except IndexError:
            if default is NotImplemented:
                raise
            else:
                return default
        return field_value.message

    def get_values(self):
        return [
            self.convert(field_value.value)
            for field_value in self.values
        ]

    def _can_this_be_edited(self, force):
        return force is True or self.ignore is False

    def set_values(self, values, force=False):
        if not self._can_this_be_edited(force):
            return
        self.values = []
        for value in values:
            self.values.append(
                FieldValue(
                    self,
                    value
                )
            )

    def set_value(self, value, index=0, force=False):
        if not self._can_this_be_edited(force):
            return
        try:
            field_value = self.values[index]
            field_value.value = self.convert.back(value)
        except IndexError:
            self.values.append(
                FieldValue(
                    self,
                    self.convert.back(value)
                ))

    def get_name(self):
        return self.name


class TreeField(Field):

    def get_name(self):
        data = {
            'name': self.name,
            'parents': self.form._get_parents(),
        }
        json = dumps(data)
        return urlsafe_b64encode(json.encode())


class FieldValue(object):

    def __init__(self, field, value):
        self.field = field
        self.value = value
        self.error = False
        self.message = None

    def set_error(self, message):
        self.error = True
        self.field.error = True
        self.message = Message()
        self.message.init(message, field=self.field, value=self)
