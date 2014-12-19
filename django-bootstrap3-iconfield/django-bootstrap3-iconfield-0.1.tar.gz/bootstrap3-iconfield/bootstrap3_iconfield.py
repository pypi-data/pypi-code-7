# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings


# Default settings
BOOTSTRAP3_ICONFIELD_DEFAULTS = {
    'error_icon_class': 'glyphicon glyphicon-remove-sign',
    'help_icon_class': 'glyphicon glyphicon-question-sign',
}

# Start with a copy of default settings
BOOTSTRAP3_ICONFIELD = BOOTSTRAP3_ICONFIELD_DEFAULTS.copy()

# Override with user settings from settings.py
BOOTSTRAP3_ICONFIELD.update(getattr(settings, 'BOOTSTRAP3_ICONFIELD', {}))


def get_bootstrap_iconfield_setting(setting, default=None):
    """
    Read a setting
    """
    return BOOTSTRAP3_ICONFIELD.get(setting, default)
