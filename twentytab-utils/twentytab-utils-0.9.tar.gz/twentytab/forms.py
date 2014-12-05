from django import forms
from twentytab.widgets import NullCheckboxWidget


class NullTrueField(forms.NullBooleanField):
    """
    A field whose valid values are True and False as None. Invalid values are
    cleaned to None.
    """
    widget = NullCheckboxWidget
