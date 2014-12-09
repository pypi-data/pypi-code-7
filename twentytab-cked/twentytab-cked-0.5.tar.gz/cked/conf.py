from appconf import AppConf
from django.conf import settings
import os


class CKEDConf(AppConf):
    STATIC_URL = u'/static/'
    MEDIA_URL = u'/media/'
    MEDIA_ROOT = u'media'
    ELFINDER_OPTIONS = {
        'root': os.path.join(os.getcwd(), 'media', 'uploads'),
        'URL': '/media/uploads/',
    }

    def configure_static_url(self, value):
        if not getattr(settings, 'STATIC_URL', None):
            self._meta.holder.STATIC_URL = value
            return value
        return getattr(settings, 'STATIC_URL')

    def configure_media_url(self, value):
        if not getattr(settings, 'MEDIA_URL', None):
            self._meta.holder.MEDIA_URL = value
            return value
        return getattr(settings, 'MEDIA_URL')

    def configure_media_root(self, value):
        if not getattr(settings, 'MEDIA_ROOT', None):
            self._meta.holder.MEDIA_ROOT = value
            return value
        return getattr(settings, 'MEDIA_ROOT')

    def configure_elfinder_options(self, value):
        if not os.path.exists(os.path.join(os.getcwd(), 'media', 'uploads')):
            os.makedirs(os.path.join(os.getcwd(), 'media', 'uploads'))
        if not getattr(settings, 'ELFINDER_OPTIONS', None):
            self._meta.holder.ELFINDER_OPTIONS = value
            return value
        return getattr(settings, 'ELFINDER_OPTIONS')