import os
from django.utils.translation import ugettext_lazy as _
from django.db import models
from mediastore.conf import settings
from mediastore.fields import FileField
from mediastore.models import Media
from mediastore.utils.files import get_file_extension


ALLOWED_EXTENSIONS = getattr(settings, 'MEDIASTORE_AUDIO_ALLOWED_FILEXTENSIONS', None)


class Audio(Media):
    help_text = _('Stores an audio file and stores its file extension.')

    file = FileField(_('audio'),
        allowed_extensions=ALLOWED_EXTENSIONS,
        upload_to=os.path.join(settings.MEDIASTORE_FS_PREFIX, 'audio')
    )
    file_extension = models.CharField(_('file extension'), max_length=12,
        null=True, blank=True, editable=False)

    class Meta:
        app_label = 'mediastore'
        verbose_name = _('audio')
        verbose_name_plural = _('audio')

    def save(self, *args, **kwargs):
        self.file_extension = get_file_extension(self.file.name)
        super(Audio, self).save(*args, **kwargs)

