# -*- coding: utf-8 -*-

# $Id$

"""This module defines functions to load the configuration options
stored in a json file.

The schema for the configuracion file:


:command: string, required. The shell command to execute whenever a
          file change is detected

:include_files_regex: list of strings, required. List of shell
          patterns, only matching files will be monitored.

:exclude_files_regex: list of strings, optional, default []. List of
          shell patterns, if a file matches it will not be monitored.

"""

import json

from arv.autotest.utils import NoDefault
from arv.autotest import validators as V


class ConfigurationError(Exception):
    pass

WATCH_NODE_SCHEMA = {
    "path" : (NoDefault, V.is_dir),
    "recurse": (True, V.is_bool),
    "auto_add": (True, V.is_bool),
    "include": ([], V.is_list_of(V.is_regex)),
    "exclude": ([], V.is_list_of(V.is_regex))
}

watch_node_validator = V.make_validator_from_schema(WATCH_NODE_SCHEMA)

THROTTLING_SCHEMA = {
    "max_events_second" : (1, V.is_int)
}

throttling_schema_validator = V.make_validator_from_schema(THROTTLING_SCHEMA)

PREPROCESSOR_ACTION_SCHEMA = {
    "regex" : (NoDefault, V.is_regex),
    "action": (NoDefault, V.is_unicode),
    "params": (None, None)
}

preprocessor_action_validator = V.make_validator_from_schema(PREPROCESSOR_ACTION_SCHEMA)

preprocessor_validator = V.is_list_of(preprocessor_action_validator)

SCHEMA = {
    # option : (default_value, validator_or_None)
    "command" : (NoDefault, None),
    "watch" : ([], V.is_list_of(watch_node_validator)),
    "global_ignore" : ([], V.is_list_of(V.is_regex)),
    "throttling" : (None, throttling_schema_validator),
    "preprocessor" : ([], preprocessor_validator)
}


def _parse_config(config, schema=SCHEMA):
    try:
        options = json.loads(config)
    except ValueError as e:
        raise ConfigurationError("Error parsing config file: %s" % e)
    validator = V.make_validator_from_schema(schema)
    try:
        cfg = validator(options)
    except ValueError as e:
        raise ConfigurationError("Error validating config file: %s " % e)
    return cfg

def read_config(path, schema=SCHEMA):
    """Read the configuracion from a file.

    Read the configuration from the file ``path``. Optionally an
    schema defining the option names, default values and validators
    can be specified in the ``schema`` parameter.

    :param path: path of the configuration file

    :param schema: a dictionary mapping the option name to a two-tuple
                   ``(default, validator)``. Used to ensure that the
                   configuration is correct. USE WITH CARE.

    :raises: ConfigurationError if the file does not exist or it is
             not a valid configuration file.
    :returns: an object with each option stored in an attribute
    :rtype: Bunch

    """
    try:
        with open(path) as f:
            return _parse_config(f.read(), schema)
    except IOError:
        raise ConfigurationError("No such file: '%s'" % path)
