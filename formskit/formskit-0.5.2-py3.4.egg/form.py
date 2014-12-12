from base64 import urlsafe_b64decode
from copy import deepcopy
from json import loads
import binascii

from .field import Field, TreeField
from .formvalidators import FormValidationError
from .messages import Message


class Form(object):

    form_name_value = 'form_name'

    def get_name(self):
        return self.__class__.__name__

    def __init__(self):
        self._init_before_create()
        self.create_form()
        self.reset()

    def _init_before_create(self):
        self.fields = {}
        self.form_validators = []
        self.raw_data = None
        self.index = None

    def add_field_object(self, field):
        self.fields[field.name] = field
        field.init_form(self)

    def add_field(self, *args, **kwargs):
        field = Field(*args, **kwargs)
        self.add_field_object(field)
        return field

    def __call__(self, raw_data):
        if self._is_form_submitted(raw_data):
            self._parse_raw_data(raw_data)
            if self._validate():
                self.submit()
                return True
            else:
                return False
        else:
            return None

    def _is_form_submitted(self, raw_data):
        return raw_data.get(self.form_name_value, None) == [self.get_name(), ]

    def _parse_raw_data(self, raw_data):
        for name, values in raw_data.items():
            if name == self.form_name_value:
                continue
            field = self._get_field(name)
            field.set_values(values)

    def _get_field(self, name):
        try:
            return self.fields[name]
        except KeyError:
            raise WrongValueName(name)

    def reset(self):
        self.success = None
        self.message = None
        for field in self.fields.values():
            field.reset()

    def _validate(self):
        # Why this method was implemented in this way?
        # Goal was to run validation on fields and if it succeeded, then form
        # can run form validators.
        # But sub_forms should always run validation.
        self.success = True
        self.success &= (
            self._validate_fields()
            and self._validate_form_validators()
        )
        return self.success

    def _validate_fields(self):
        success = True
        for field in self.fields.values():
            success &= field.validate()
        return success

    def create_form(self):
        pass

    def _validate_form_validators(self):
        try:
            for validator in self.form_validators:
                validator()
        except FormValidationError as er:
            self.message = Message()
            self.message.init(er.message, form=self)
            return False
        return True

    def add_form_validator(self, validator):
        validator.set_form(self)
        self.form_validators.append(validator)

    def get_values(self, name):
        return self.fields[name].get_values()

    def get_value(self, name, index=0, default=NotImplemented):
        return self.fields[name].get_value(index, default)

    def set_values(self, name, values, force=False):
        self.fields[name].set_values(values, force=force)

    def set_value(self, name, value, index=0, force=False):
        self.fields[name].set_value(value, index, force=force)

    def submit(self):
        pass

    def get_data_dict(self, minified=False):
        tree = {}
        for name, field in self.fields.items():
            tree[name] = field.get_values()
            if minified and len(tree[name]) == 1:
                tree[name] = tree[name][0]
            elif minified and len(tree[name]) == 0:
                del tree[name]
        return tree

    def parse_dict(self, data):
        for name, values in data.items():
            if name in self.fields:
                field = self.fields[name]
                if hasattr(values, '__iter__') and type(values) is not str:
                    field.set_values(values)
                else:
                    field.set_value(values)
            else:
                self._parse_sub_form(name, values)


class TreeForm(Form):

    def _init_before_create(self):
        super()._init_before_create()
        self.parent = None
        self.childs = {}

    def add_field(self, *args, **kwargs):
        field = TreeField(*args, **kwargs)
        self.add_field_object(field)
        return field

    def reset(self):
        super().reset()
        for name in self.childs:
            self.childs[name] = {0: self.childs[name][0]}
            self.childs[name][0].reset()

    def _get_parents(self):
        if self.parent is None:
            return [self._get_form_info()]
        else:
            parents = self.parent._get_parents()
            parents.append(self._get_form_info())
            return parents

    def _get_form_info(self):
        return {
            'name': self.get_name(),
            'index': self.index}

    def add_sub_form(self, form):
        form._set_parent(self, 0)
        self.childs[form.get_name()] = {0: form}

    def _set_parent(self, parent, index):
        self.parent = parent
        self.index = index

    def get_or_create_sub_form(self, name, index):
        try:
            return self.get_sub_form(name, index)
        except KeyError:
            form = self._clone_sub_form(name)
            self.childs[name][index] = form
            form.index = index
            return form

    def get_sub_form(self, name, index):
        return self.childs[name][index]

    def _clone_sub_form(self, name):
        form = self.childs[name][0]
        form = deepcopy(form)
        form.reset()
        return form

    def _validate_sub_forms(self):
        success = True
        for sub_forms in self.childs.values():
            for sub_form in sub_forms.values():
                success &= sub_form._validate_fields()
        return success

    def _parse_sub_form(self, name, data):
        for index, values in enumerate(data):
            sub_form = self.get_or_create_sub_form(name, index)
            sub_form.parse_dict(values)

    def _validate(self):
        # Why this method was implemented in this way?
        # Goal was to run validation on fields and if it succeeded, then form
        # can run form validators.
        # But sub_forms should always run validation.
        super()._validate()
        self.success &= self._validate_sub_forms()
        return self.success

    def _get_field(self, name):
        data = self._decode_name(name)
        name = data['name']

        form = self._get_sub_form(data['parents'][1:])
        return form.fields[name]

    def get_data_dict(self, minified=False):
        tree = super().get_data_dict(minified=minified)
        for name, sub_forms in self.childs.items():
            tree[name] = {}
            for index, sub_form in sub_forms.items():
                tree[name][index] = sub_form.get_data_dict(minified)
        return tree

    def _decode_name(self, name):
        try:
            json = urlsafe_b64decode(name).decode('utf8')
            return loads(json)
        except (binascii.Error, UnicodeDecodeError):
            raise WrongValueName(name)

    def _get_sub_form(self, parents):
        if parents == []:
            return self
        form_name = parents[0]['name']
        index = parents[0]['index']
        sub_form = self.get_or_create_sub_form(form_name, index)
        return sub_form._get_sub_form(parents[1:])


class WrongValueName(Exception):

    def __init__(self, name):
        self.name = name
