"""
Contains some fields as utilities.
"""
from django.db import models
from django.utils.text import capfirst
from twentytab import forms
from twentytab.countries import CONTINENT_COUNTRIES, COUNTRIES


class NullTrueFieldBase(models.SubfieldBase):
    def to_python(self, value):
        return value == True


class NullTrueField(models.NullBooleanField):
    __metaclass__ = NullTrueFieldBase

    def to_python(self, value):
        if value is True:
            return value
        return False

    def get_prep_value(self, value):
        if value is None or value is False:
            return None
        return True

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.NullTrueField,
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text}
        defaults.update(kwargs)
        return super(NullTrueField, self).formfield(**defaults)


class CountryField(models.CharField):
    """
    Is a CharField with the complete list of countries as choices.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault(u'max_length', 2)
        kwargs.setdefault(u'choices', COUNTRIES)

        super(CountryField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        """
        Returns internal type of this field: CharField as string
        """
        return "CharField"


class ContinentCountryField(models.CharField):
    """
    Is a CharField with the complete list of countries as choices.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault(u'max_length', 2)
        kwargs.setdefault(u'choices', CONTINENT_COUNTRIES)

        super(ContinentCountryField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        """
        Returns internal type of this field: CharField as string
        """
        return "CharField"


try:
    from south.modelsinspector import add_introspection_rules

    add_introspection_rules([],
        ["^twentytab\.fields\.ContinentCountryField", "^twentytab\.fields\.CountryField",
         "^twentytab\.fields\.NullTrueField"])
except ImportError:
    pass