"""
Load config ('gnip_config.ini') for script use
Credit: https://github.com/praw-dev/praw/blob/master/praw/settings.py
"""

import os
import sys

try:
    import ConfigParser as configparser
except ImportError:
    import configparser


def _load_configuration():
    config = configparser.RawConfigParser()
    module_dir = os.path.dirname(sys.modules[__name__].__file__)
    if 'APPDATA' in os.environ:  # Windows
        os_config_path = os.environ['APPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:  # Modern Linux
        os_config_path = os.environ['XDG_CONFIG_HOME']
    elif 'HOME' in os.environ:  # Legacy Linux
        os_config_path = os.path.join(os.environ['HOME'], '.config')
    else:
        os_config_path = None
    locations = [os.path.join(
        module_dir, 'gnip_config.ini'), 'gnip_config.ini']
    if os_config_path is not None:
        locations.insert(1, os.path.join(os_config_path, 'gnip_config.ini'))
    if not config.read(locations):
        raise Exception('Could not find config file in any of: %s' % locations)
    return config

PYGNIP_CONFIG = _load_configuration()
