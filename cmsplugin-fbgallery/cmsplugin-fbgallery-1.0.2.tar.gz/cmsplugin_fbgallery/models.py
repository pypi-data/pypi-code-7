from django.db import models
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _


class FacebookGallery(CMSPlugin):
    album_id = models.CharField(_('Album Id'), max_length=500)
    album_name = models.CharField(_('Album Name'), max_length=100)

