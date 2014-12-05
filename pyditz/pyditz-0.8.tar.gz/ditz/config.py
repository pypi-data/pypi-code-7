"""
Configuration file.
"""

import os
import re
import warnings
import six

import pkg_resources as pkg
from six.moves import configparser as conf

from .pkginfo import __title__
from .logger import log


class DitzConfig(conf.SafeConfigParser):
    def __init__(self):
        conf.SafeConfigParser.__init__(self)
        defaults = pkg.resource_filename(__name__, "config.cfg")
        with open(defaults) as fp:
            self.readfp(fp)

    def write_file(self, path):
        """Write config data to file."""

        with open(path, "w") as fp:
            fp.write("# %s configuration file.\n\n" % __title__)
            self.write(fp)


class Config(object):
    def __init__(self):
        self.path = get_userconfig()
        self.parser = None

    def set_file(self, path):
        self.path = path

    def set_option(self, setting):
        m = re.match(r'(\w+)\.(\w+)=(.*)', setting)
        if m:
            section, option, value = m.groups()
        else:
            raise ValueError("'%s': expected 'section.option=value'"
                             % setting)

        try:
            self.set(section, option, value)
        except conf.NoSectionError:
            raise ValueError("'%s': no such config section" % section)

    def __getattr__(self, attr):
        if not self.parser:
            self.parser = DitzConfig()
            log.info("reading %s" % self.path)
            self.parser.read(self.path)

        return getattr(self.parser, attr)


class ConfigSection(object):
    """
    Wrapper to the config file which looks up a particular section.
    """

    def __init__(self, name, section, config):
        self.name = name
        self.config = config
        self.section = section

    def add(self, name, default):
        name = self.option(name)
        if not self.config.has_option(self.section, name):
            self.config.set(self.section, name, default)

    def get(self, name):
        """
        Get the named configuration value as a string.
        """

        return self.config.get(self.section, self.option(name))

    def getint(self, name):
        """
        Get the named configuration value as an integer.
        """

        return self.config.getint(self.section, self.option(name))

    def getfloat(self, name):
        """
        Get the named configuration value as a float.
        """

        return self.config.getfloat(self.section, self.option(name))

    def getboolean(self, name):
        """
        Get the named configuration value as a boolean.
        """

        return self.config.getboolean(self.section, self.option(name))

    def option(self, name):
        return self.name + "_" + name


def config_path(filename=None):
    "Return a pathname in the user's config directory."

    parts = [os.path.expanduser("~"), ".ditz"]

    if filename:
        parts.append(filename)

    return os.path.join(*parts)


def get_userconfig():
    "Return pathname of user config file."

    # Warn about old ~/.ditzrc if it exists.
    homedir = os.path.expanduser("~")
    path = os.path.join(homedir, ".ditzrc")
    if os.path.exists(path):
        warn("Move deprecated ~/.ditzrc file to ~/.ditz/ditz.cfg")
        return path

    # Try standard config file.
    return config_path("ditz.cfg")


def warn(msg):
    "Warn about obsolete configuration."
    warnings.warn(msg, UserWarning, stacklevel=2)


# Ditz user config settings.
config = Config()
