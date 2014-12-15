# -*- coding: utf-8 -*-
import os
from django.utils.translation import ugettext_lazy as _
from django.db import models
from mediastore.conf import settings
from mediastore.models import Media


THUMBNAIL_UPLOAD_DIR = os.path.join(
    settings.MEDIASTORE_FS_PREFIX, 'embeded/thumbnails')


class Embeded(Media):
    content = models.TextField()
    thumbnail = models.ImageField(
        upload_to=THUMBNAIL_UPLOAD_DIR,
        null=True, blank=True)

    class Meta:
        app_label = 'mediastore'
        verbose_name = _('embeded media')
        verbose_name_plural = _('embeded media')
