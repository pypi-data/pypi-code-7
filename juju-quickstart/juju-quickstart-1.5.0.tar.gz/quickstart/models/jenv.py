# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2014 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License version 3, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Juju Quickstart jenv generated files handling.

At bootstrap, Juju writes a generated file (jenv) located in JUJU_HOME.
This module includes functions to load and parse those jenv file contents.
"""

from __future__ import unicode_literals

import os

from quickstart import (
    serializers,
    settings,
)


def exists(env_name):
    """Report whether the jenv generated file exists for the given env_name."""
    jenv_path = _get_jenv_path(env_name)
    return os.path.isfile(jenv_path)


def get_value(env_name, *args):
    """Read a value from the Juju generated environment file (jenv).

    Return the value corresponding to the section specified in args.
    For instance, calling get_value('ec2', 'bootstrap-config', 'admin-secret')
    returns the value associated with the "admin-secret" key included on the
    "bootstrap-config" section of the jenv file.

    Raise a ValueError if:
        - the environment file is not found;
        - the environment file contents are not parsable by YAML;
        - the YAML contents are not properly structured;
        - one the keys in args is not found.
    """
    jenv_path = _get_jenv_path(env_name)
    data = serializers.yaml_load_from_path(jenv_path)
    section = 'root'
    for key in args:
        try:
            data = data[key]
        except (KeyError, TypeError):
            msg = ('invalid YAML contents in {}: ''{} key not found in the {} '
                   'section'.format(jenv_path, key, section))
            raise ValueError(msg.encode('utf-8'))
        section = key
    return data


def _get_jenv_path(env_name):
    """Return the path to the generated jenv file for the given env_name."""
    filename = '{}.jenv'.format(env_name)
    path = os.path.join(settings.JUJU_HOME, 'environments', filename)
    return os.path.expanduser(path)
