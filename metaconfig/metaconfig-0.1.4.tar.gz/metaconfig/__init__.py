# BSD Licence
# Copyright (c) 2010, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

"""
State global to the whole package.

"""

import sys, re, os
from ConfigParser import ConfigParser

from metaconfig.mconf import MetaConfig, Error
from metaconfig.decorator import ConfigDecorator

import logging
log = logging.getLogger(__name__)

_metaconfig = None

def _default_search_path():
    search_path = [
        './metaconfig.conf',
        os.path.join(os.environ.get('HOME', ''), '.metaconfig.conf'),
        os.path.join(sys.prefix, 'etc', 'metaconfig.conf')
        ]
    if 'METACONFIG_CONF' in os.environ:
        search_path[0:] = [(os.environ['METACONFIG_CONF'])]

    return search_path

def init_from_config(config):
    """
    Initialise metaconfig from a :mod:`ConfigParser.ConfigParser` instance.

    An exception will be raised if metaconfig has already been initialised.

    """

    global _metaconfig

    if _metaconfig is not None:
        raise Exception("Metaconfig is already initialised")

    _metaconfig = MetaConfig.from_config(config)

def init_from_string(config_str):
    """
    Initialise metaconfig from a string.

    An exception will be raised if metaconfig has already been initialised.

    """
    from StringIO import StringIO
    mconf = ConfigParser()
    mconf.readfp(StringIO(config_str))
    init_from_config(mconf)

def init(search_path=None):
    """
    Initialise metaconfig.

    An exception will be raised if metaconfig has already been initialised.

    :param search_path: A sequence of file paths to search for a metaconfig
        configuration.

    If ``search_path`` is None it defaults to:

    1. The value of the ``METACONFIG_CONF`` environment variable if set.
    2. ``metaconfig.conf`` in the current directory.
    3. ``$HOME/.metaconfig.conf``
    4. ``<sys.prefix>/etc/metaconfig.conf``

    """

    global _metaconfig

    if _metaconfig is not None:
        raise Exception("Metaconfig is already initialised")

    if search_path is None:
        search_path = _default_search_path()
    for config in search_path:
        if os.path.exists(config):
            log.debug('Selected %s as metaconfig.conf' % config)
            _metaconfig = MetaConfig.from_config_file(config)
            return
    else:
        _metaconfig = MetaConfig()
    

def get_config(name, inherit=True):
    """
    Returns the :mod:`ConfigParser.ConfigParser` for the given name.

    :param name: The name of the config object to return.  This is interpreted
        as a '.'-separated hierarchical namespace.
    :param inherit: If ``True`` and cofig ``name`` does not exist each config
        above ``name`` in the hierarchy will be tried before returning an empty
        config object.  For instance ``get_config("x.y.z")`` would try to 
        return existing configs ``x.y.z``, ``x.y`` and ``x`` before returning a
        new, empty config ``x.y.z``.

    """

    if _metaconfig is None:
        init()

    return _metaconfig.get_config(name, inherit=inherit)

def add_config(name, config_parser):
    """
    Add a config_parser object to metaconfig.

    """

    if _metaconfig is None:
        init()

    return _metaconfig.add_config(name, config_parser)

def add_config_file(name, config, ConfigClass=None):
    """
    Read a config file and add it to metaconfig.

    """

    if _metaconfig is None:
        init()

    return _metaconfig.add_config_file(name, config, ConfigClass)


def reset():
    global _metaconfig

    log.warn("Reseting metaconfig.  Existing configs will remain.")

    _metaconfig = None
