# -*- coding: utf-8 -*-
class SettingsProxy(object):
    def __init__(self, settings, defaults):
        self.settings = settings
        self.defaults = defaults

    def __getattr__(self, attr):
        try:
            return getattr(self.settings, attr)
        except AttributeError:
            try:
                return getattr(self.defaults, attr)
            except AttributeError:
                raise AttributeError, 'settings object has no attribute "%s"' % attr


class defaults(object):
    MEDIASTORE_FS_PREFIX = 'media'


from django.conf import settings as django_settings
settings = SettingsProxy(django_settings, defaults)
