# -*- coding: utf-8 -*-
from django import forms
from sortedm2m.forms import SortedMultipleChoiceField
from mediastore.models import Media
from mediastore.widgets import MediaSelect, MediaSelectMultiple


__all__ = (
    'MediaChoiceField',
    'MediaMultipleChoiceField')


class MediaChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        mediatype = kwargs.pop('mediatype', None)
        queryset = Media.objects.all()
        if mediatype:
            queryset = queryset.type(mediatype)
        kwargs.setdefault('queryset', queryset)
        from django.db import models
        if mediatype:
            db_field = models.ForeignKey(Media, limit_choices_to={'type': mediatype})
        else:
            db_field = models.ForeignKey(Media)
        kwargs.setdefault('widget', MediaSelect(db_field.rel, mediatype=mediatype))
        super(MediaChoiceField, self).__init__(*args, **kwargs)


class MediaMultipleChoiceField(SortedMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        self.rel = kwargs.pop('rel')
        self.sorted = kwargs.pop('sorted', False)
        mediatype = kwargs.pop('mediatype', None)
        queryset = Media.objects.all()
        if mediatype:
            queryset = queryset.type(mediatype)
        kwargs.setdefault('queryset', queryset)
        kwargs.setdefault('widget', MediaSelectMultiple(rel=self.rel, mediatype=mediatype, sorted=self.sorted))
        super(MediaMultipleChoiceField, self).__init__(*args, **kwargs)
