# -*- coding: utf-8 -*-
from django.db import models
from sortedm2m.fields import SortedManyToManyField
from mediastore.forms import MediaMultipleChoiceField
from mediastore.widgets import MediaSelect, MediaSelectMultiple


class MediaField(models.ForeignKey):
    def __init__(self, **kwargs):
        from mediastore.models import Media
        kwargs['to'] = Media
        super(MediaField, self).__init__(**kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'widget': MediaSelect(
                rel=self.rel,
                **kwargs.pop('widget_kwargs', {})),
        }
        defaults.update(kwargs)
        return super(MediaField, self).formfield(**defaults)


class MultipleMediaField(SortedManyToManyField):
    def __init__(self, to=None, sorted=False, *args, **kwargs):
        if to is None:
            from mediastore.models import Media
            to = Media
        super(MultipleMediaField, self).__init__(to, sorted, *args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': MediaMultipleChoiceField,
            'rel': self.rel,
            'widget': MediaSelectMultiple(
                rel=self.rel,
                sorted=self.sorted,
                **kwargs.pop('widget_kwargs', {})),
            'sorted': self.sorted,
        }
        defaults.update(kwargs)
        return super(MultipleMediaField, self).formfield(**defaults)


try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    add_introspection_rules = None

if add_introspection_rules:
    add_introspection_rules([
        (
            [MediaField],
            [],
            {},
        ),
    ], ["^mediastore\.fields\.related\.MediaField"])


    add_introspection_rules([
        (
            [MultipleMediaField],
            [],
            {'to': ('rel.to', {'default': 'mediastore.Media'})},
        ),
    ], ["^mediastore\.fields\.related\.MultipleMediaField"])
