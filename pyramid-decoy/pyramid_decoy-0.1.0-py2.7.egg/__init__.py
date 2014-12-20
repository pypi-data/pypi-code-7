# Copyright (c) 2014 by pyramid_decoy authors and contributors
# <see AUTHORS file>
#
# This module is part of pyramid_decoy and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Main decoy module."""

import logging

__version__ = '0.1.0'


logger = logging.getLogger(__name__)


SETTINGS_PREFIX = 'decoy'


def includeme(configurator):
    """
    Configure decoy plugin on pyramid application.

    :param pyramid.configurator.Configurator configurator: pyramid's
        configurator object
    """
    configurator.registry['decoy'] = get_decoy_settings(
        configurator.get_settings()
    )
    configurator.add_route('decoy', pattern='/*p')
    configurator.add_view('pyramid_decoy.views.decoy', route_name='decoy')


def get_decoy_settings(settings):
    """
    Extract decoy settings out of all.

    :param dict settings: pyramid app settings
    :returns: decoy settings
    :rtype: dict
    """
    return {
        k.split('.', 1)[-1]: v
        for k, v in settings.items()
        if k[:len(SETTINGS_PREFIX)] == SETTINGS_PREFIX
    }
