import os
from django.utils.translation import ugettext_lazy as _
from django.db import models
from mediastore.conf import settings
from mediastore.models import Media


def get_image_mimetype(file):
    try:
        from PIL import Image
    except ImportError:
        import Image
    closed = file.closed
    try:
        if closed:
            file.open()
        image = Image.open(file)
    except IOError:
        return None
    if closed:
        file.close()
    elif hasattr(file, 'seek'):
        file.seek(0)
    return Image.MIME[image.format]


class Image(Media):
    help_text = _('Stores an image and holds attributes like width, height and mimetype.')

    file = models.ImageField(_('image'),
        width_field='width',
        height_field='height',
        upload_to=os.path.join(settings.MEDIASTORE_FS_PREFIX, 'images')
    )
    width = models.IntegerField(_('width'), editable=False)
    height = models.IntegerField(_('height'), editable=False)
    mimetype = models.CharField(_('mimetype'), max_length=32,
        null=True, blank=True, editable=False)

    class Meta:
        app_label = 'mediastore'
        verbose_name = _('image')
        verbose_name_plural = _('images')

    def save(self, *args, **kwargs):
        self.mimetype = get_image_mimetype(self.file)
        super(Image, self).save(*args, **kwargs)
