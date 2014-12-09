from django.db import models
from django import forms
from cked.widgets import CKEditorWidget


class RichTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop("config", None)
        super(RichTextField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': RichTextFormField,
            'config': self.config
        }
        defaults.update(kwargs)
        return super(RichTextField, self).formfield(**defaults)


class RichTextFormField(forms.fields.CharField):
    def __init__(self, config=None, *args, **kwargs):
        kwargs.update({'widget': CKEditorWidget(config=config)})
        super(RichTextFormField, self).__init__(*args, **kwargs)

# Fix field for South
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^cked\.fields\.RichTextField"])
except:
    pass
