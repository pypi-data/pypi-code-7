from wtforms import *

class FormDataMultiDict(object):

    def __init__(self, multidict):
        self._wrapped = multidict

    def __iter__(self):
        return iter(self._wrapped)

    def __len__(self):
        return len(self._wrapped)

    def __contains__(self, name):
        return (name in self._wrapped)

    def __getitem__(self, name):
        return self._wrapped[name]

    def __getattr__(self, name):
        return self.__getitem__(name)

    def getlist(self, name):
        if name not in self._wrapped:
            return []
        if isinstance(self._wrapped[name], list):
            return self._wrapped[name]
        return [self._wrapped[name]]

class RequestForm(Form):
    def __init__(self, controller, formdata=None, obj=None, prefix='', **kwargs):
        self._delimiter_start = '<p>'
        self._delimiter_end = '</p>'
        self.controller = controller
        super().__init__(FormDataMultiDict(formdata), obj, prefix, **kwargs)

    def set_error_delimiter(self, start, end):
        self._delimiter_start = start
        self._delimiter_end = end

    def validation_errors(self):
        error_string = ''
        for e in self.errors.values():
            error_string += (self._delimiter_start + (self._delimiter_end + self._delimiter_start).join(e) + self._delimiter_end)
        return error_string

    @property
    def errors(self):
        if self._errors is None:
            for field_id in super().errors.keys():
                for k, v in enumerate(self._errors[field_id]):
                    self._errors[field_id][k] = v.replace('{{field_label}}', self._fields[field_id].label.text)
        return self._errors