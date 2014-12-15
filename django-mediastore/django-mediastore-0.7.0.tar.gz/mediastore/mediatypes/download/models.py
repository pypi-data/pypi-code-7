# -*- coding: utf-8 -*-
import os
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mediastore.conf import settings
from mediastore.models import Media


def get_file_extension(file):
    bits = file.name.split('.',-1)
    if len(bits) == 1:
        return ''
    else:
        return bits[-1].lower()

class Download(Media):
    help_text = _('Stores an downloadable file, its file extension and the file size.')

    file = models.FileField(_('download file'),
        upload_to=os.path.join(settings.MEDIASTORE_FS_PREFIX, 'downloads')
    )
    file_extension = models.CharField(_('file extenstion'), max_length=12,
        null=True, blank=True, editable=False)
    file_size = models.PositiveIntegerField(_('file size'), editable=False)
    count = models.PositiveIntegerField(_(u'download counter'), default=0)

    class Meta:
        app_label = 'mediastore'
        verbose_name = _('download')
        verbose_name_plural = _('downloads')

    def save(self, *args, **kwargs):
        self.file_extension = get_file_extension(self.file)
        self.file_size = self.file.size
        super(Download, self).save(*args, **kwargs)

    def get_download_link(self):
        try:
            url = reverse('mediastore-download-link', args=(
                self.slug, os.path.basename(self.file.name)))
        except NoReverseMatch, e:
            url = self.file.url
        return url
