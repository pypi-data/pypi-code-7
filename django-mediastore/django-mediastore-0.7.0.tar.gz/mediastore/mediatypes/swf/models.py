# -*- coding: utf-8 -*-
import os
from django.utils.translation import ugettext_lazy as _
from django.db import models
from mediastore.conf import settings
from mediastore.models import Media


class SWF(Media):
    help_text = _('Stores a swf file.')

    file = models.FileField(_('swf file'),
        upload_to=os.path.join(settings.MEDIASTORE_FS_PREFIX, 'swf')
    )
    width = models.PositiveIntegerField(_('width'), null=True, blank=True)
    height = models.PositiveIntegerField(_('height'), null=True, blank=True)

    class Meta:
        app_label = 'mediastore'
        verbose_name = _('SWF')
        verbose_name_plural = _('SWFs')
