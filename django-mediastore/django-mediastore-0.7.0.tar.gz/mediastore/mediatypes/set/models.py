# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mediastore.models import Media
from mediastore.fields.related import MediaField, MultipleMediaField


class Set(Media):
    preview = MediaField(
        related_name='sets_preview',
        null=True, blank=True)
    media = MultipleMediaField(related_name='sets')

    class Meta:
        app_label = 'mediastore'
        verbose_name = _('set')
        verbose_name_plural = _('sets')

    def __iter__(self):
        return iter(self.media.all().select_subclasses())

    def __len__(self):
        return self.media.count()
