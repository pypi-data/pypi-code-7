# -*- coding: utf-8 -*-
import os
from django.utils.translation import ugettext_lazy as _
from django.db import models
from mediastore.conf import settings
from mediastore.models import Media


class PDF(Media):
    help_text = _('Stores a pdf file and the file size.')

    file = models.FileField(_('pdf file'),
        upload_to=os.path.join(settings.MEDIASTORE_FS_PREFIX, 'pdf')
    )
    file_size = models.PositiveIntegerField(_('file size'), editable=False)

    class Meta:
        app_label = 'mediastore'
        verbose_name = _('PDF')
        verbose_name_plural = _('PDFs')

    def save(self, *args, **kwargs):
        self.file_size = self.file.size
        super(PDF, self).save(*args, **kwargs)
