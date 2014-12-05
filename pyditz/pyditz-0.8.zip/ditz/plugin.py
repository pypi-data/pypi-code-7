"""
A simple plugin system.

Inspiration:

* http://martyalchin.com/2008/jan/10/simple-plugin-framework
* https://pypi.python.org/pypi/pluginloader
"""

import os
import pkg_resources as pkg

from six import add_metaclass

from .logger import log


class PluginLoader(object):
    def __init__(self):
        #: List of paths and entrypoints to load.
        self.loading = []

        #: Set of paths and entrypoints already loaded.
        self.loaded = set()

    def add_path(self, path):
        "Add a path to the load list."
        self.loading.append(('path', path))

    def add_entrypoint(self, group):
        "Add an entrypoint group to the load list."
        self.loading.append(('entrypoint', group))

    def load(self):
        "Load all plugins."

        for tag, name in self.loading:
            if tag == 'path':
                self.load_directory(name)
            elif tag == 'entrypoint':
                for entrypoint in pkg.iter_entry_points(name):
                    group = name + '.' + entrypoint.name
                    self.load_plugin(entrypoint, group)

    def load_plugin(self, entrypoint, group):
        if group not in self.loaded:
            try:
                log.info("loading plugin from entry point '%s'" % group)
                entrypoint.load()
            except Exception:
                log.exception('error loading %s (ignored)' % group)

            self.loaded.add(group)

    def load_file(self, filename, context=None):
        if filename not in self.loaded:
            log.info("loading plugins from file '%s'", filename)

            try:
                context = context or {}
                with open(filename) as fp:
                    exec(fp.read(), context)
            except Exception:
                log.exception('error loading %s (ignored)' % filename)

            self.loaded.add(filename)

    def load_directory(self, path, recursive=False, context=None):
        if path not in self.loaded and os.path.isdir(path):
            log.info("loading plugins from directory '%s'", path)

            for filename in os.listdir(path):
                fullpath = os.path.join(path, filename)

                if os.path.isfile(fullpath):
                    self.load_file(fullpath, context)
                elif os.path.isdir(fullpath):
                    if recursive:
                        self.load_directory(fullpath, recursive, context)

            self.loaded.add(path)


class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = {}
        elif hasattr(cls, 'name') and cls.name is not None:
            log.info("registering %s plugin: %s", cls.category, cls.name)
            cls.plugins[cls.category, cls.name] = cls


@add_metaclass(PluginMount)
class Plugin(object):
    #: Plugin name.  If None, it is not registered.
    name = None

    #: Plugin category.  This is set by direct subclasses which are
    #: intended to be subclassed further by third-party plugins.
    category = None

    #: One-line plugin description.  Appears in help text.
    description = "no description"

    #: Plugin version.  At the moment nothing is done with this; it's for
    #: information only.
    version = "0.1"

    #: Plugin author.  At the moment nothing is done with this; it's for
    #: information only.
    author = "unknown"

    #: Package name, if it is part of a package.  This is used to locate
    #: auxiliary files bundled in the package.
    package = None


def get_plugin(basecls, name):
    "Look up and return a plugin of a given type and name."

    for cls in get_plugins(basecls):
        if name == cls.name:
            return cls

    return None


def get_plugins(basecls):
    "Yield all plugins of a given type."

    for (name, category), cls in sorted(basecls.plugins.items()):
        if issubclass(cls, basecls):
            yield cls


# Create standard plugin loader.
loader = PluginLoader()
