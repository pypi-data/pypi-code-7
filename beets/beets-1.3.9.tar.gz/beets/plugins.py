# This file is part of beets.
# Copyright 2013, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Support for beets plugins."""

import logging
import traceback
from collections import defaultdict
import inspect

import beets
from beets import mediafile

PLUGIN_NAMESPACE = 'beetsplug'

# Plugins using the Last.fm API can share the same API key.
LASTFM_KEY = '2dc3914abf35f0d9c92d97d8f8e42b43'

# Global logger.
log = logging.getLogger('beets')


class PluginConflictException(Exception):
    """Indicates that the services provided by one plugin conflict with
    those of another.

    For example two plugins may define different types for flexible fields.
    """


# Managing the plugins themselves.

class BeetsPlugin(object):
    """The base class for all beets plugins. Plugins provide
    functionality by defining a subclass of BeetsPlugin and overriding
    the abstract methods defined here.
    """
    def __init__(self, name=None):
        """Perform one-time plugin setup.
        """
        self.import_stages = []
        self.name = name or self.__module__.split('.')[-1]
        self.config = beets.config[self.name]
        if not self.template_funcs:
            self.template_funcs = {}
        if not self.template_fields:
            self.template_fields = {}
        if not self.album_template_fields:
            self.album_template_fields = {}

    def commands(self):
        """Should return a list of beets.ui.Subcommand objects for
        commands that should be added to beets' CLI.
        """
        return ()

    def queries(self):
        """Should return a dict mapping prefixes to Query subclasses.
        """
        return {}

    def track_distance(self, item, info):
        """Should return a Distance object to be added to the
        distance for every track comparison.
        """
        return beets.autotag.hooks.Distance()

    def album_distance(self, items, album_info, mapping):
        """Should return a Distance object to be added to the
        distance for every album-level comparison.
        """
        return beets.autotag.hooks.Distance()

    def candidates(self, items, artist, album, va_likely):
        """Should return a sequence of AlbumInfo objects that match the
        album whose items are provided.
        """
        return ()

    def item_candidates(self, item, artist, title):
        """Should return a sequence of TrackInfo objects that match the
        item provided.
        """
        return ()

    def album_for_id(self, album_id):
        """Return an AlbumInfo object or None if no matching release was
        found.
        """
        return None

    def track_for_id(self, track_id):
        """Return a TrackInfo object or None if no matching release was
        found.
        """
        return None

    def add_media_field(self, name, descriptor):
        """Add a field that is synchronized between media files and items.

        When a media field is added ``item.write()`` will set the name
        property of the item's MediaFile to ``item[name]`` and save the
        changes. Similarly ``item.read()`` will set ``item[name]`` to
        the value of the name property of the media file.

        ``descriptor`` must be an instance of ``mediafile.MediaField``.
        """
        # Defer impor to prevent circular dependency
        from beets import library
        mediafile.MediaFile.add_field(name, descriptor)
        library.Item._media_fields.add(name)

    listeners = None

    @classmethod
    def register_listener(cls, event, func):
        """Add a function as a listener for the specified event. (An
        imperative alternative to the @listen decorator.)
        """
        if cls.listeners is None:
            cls.listeners = defaultdict(list)
        cls.listeners[event].append(func)

    @classmethod
    def listen(cls, event):
        """Decorator that adds a function as an event handler for the
        specified event (as a string). The parameters passed to function
        will vary depending on what event occurred.

        The function should respond to named parameters.
        function(**kwargs) will trap all arguments in a dictionary.
        Example:

            >>> @MyPlugin.listen("imported")
            >>> def importListener(**kwargs):
            ...     pass
        """
        def helper(func):
            if cls.listeners is None:
                cls.listeners = defaultdict(list)
            cls.listeners[event].append(func)
            return func
        return helper

    template_funcs = None
    template_fields = None
    album_template_fields = None

    @classmethod
    def template_func(cls, name):
        """Decorator that registers a path template function. The
        function will be invoked as ``%name{}`` from path format
        strings.
        """
        def helper(func):
            if cls.template_funcs is None:
                cls.template_funcs = {}
            cls.template_funcs[name] = func
            return func
        return helper

    @classmethod
    def template_field(cls, name):
        """Decorator that registers a path template field computation.
        The value will be referenced as ``$name`` from path format
        strings. The function must accept a single parameter, the Item
        being formatted.
        """
        def helper(func):
            if cls.template_fields is None:
                cls.template_fields = {}
            cls.template_fields[name] = func
            return func
        return helper


_classes = set()


def load_plugins(names=()):
    """Imports the modules for a sequence of plugin names. Each name
    must be the name of a Python module under the "beetsplug" namespace
    package in sys.path; the module indicated should contain the
    BeetsPlugin subclasses desired.
    """
    for name in names:
        modname = '%s.%s' % (PLUGIN_NAMESPACE, name)
        try:
            try:
                namespace = __import__(modname, None, None)
            except ImportError as exc:
                # Again, this is hacky:
                if exc.args[0].endswith(' ' + name):
                    log.warn(u'** plugin {0} not found'.format(name))
                else:
                    raise
            else:
                for obj in getattr(namespace, name).__dict__.values():
                    if isinstance(obj, type) and issubclass(obj, BeetsPlugin) \
                            and obj != BeetsPlugin and obj not in _classes:
                        _classes.add(obj)

        except:
            log.warn(u'** error loading plugin {0}'.format(name))
            log.warn(traceback.format_exc())


_instances = {}


def find_plugins():
    """Returns a list of BeetsPlugin subclass instances from all
    currently loaded beets plugins. Loads the default plugin set
    first.
    """
    load_plugins()
    plugins = []
    for cls in _classes:
        # Only instantiate each plugin class once.
        if cls not in _instances:
            _instances[cls] = cls()
        plugins.append(_instances[cls])
    return plugins


# Communication with plugins.

def commands():
    """Returns a list of Subcommand objects from all loaded plugins.
    """
    out = []
    for plugin in find_plugins():
        out += plugin.commands()
    return out


def queries():
    """Returns a dict mapping prefix strings to Query subclasses all loaded
    plugins.
    """
    out = {}
    for plugin in find_plugins():
        out.update(plugin.queries())
    return out


def types(model_cls):
    # Gives us `item_types` and `album_types`
    attr_name = '{0}_types'.format(model_cls.__name__.lower())
    types = {}
    for plugin in find_plugins():
        plugin_types = getattr(plugin, attr_name, {})
        for field in plugin_types:
            if field in types and plugin_types[field] != types[field]:
                raise PluginConflictException(
                    u'Plugin {0} defines flexible field {1} '
                    'which has already been defined with '
                    'another type.'.format(plugin.name, field)
                )
        types.update(plugin_types)
    return types


def track_distance(item, info):
    """Gets the track distance calculated by all loaded plugins.
    Returns a Distance object.
    """
    from beets.autotag.hooks import Distance
    dist = Distance()
    for plugin in find_plugins():
        dist.update(plugin.track_distance(item, info))
    return dist


def album_distance(items, album_info, mapping):
    """Returns the album distance calculated by plugins."""
    from beets.autotag.hooks import Distance
    dist = Distance()
    for plugin in find_plugins():
        dist.update(plugin.album_distance(items, album_info, mapping))
    return dist


def candidates(items, artist, album, va_likely):
    """Gets MusicBrainz candidates for an album from each plugin.
    """
    out = []
    for plugin in find_plugins():
        out.extend(plugin.candidates(items, artist, album, va_likely))
    return out


def item_candidates(item, artist, title):
    """Gets MusicBrainz candidates for an item from the plugins.
    """
    out = []
    for plugin in find_plugins():
        out.extend(plugin.item_candidates(item, artist, title))
    return out


def album_for_id(album_id):
    """Get AlbumInfo objects for a given ID string.
    """
    out = []
    for plugin in find_plugins():
        res = plugin.album_for_id(album_id)
        if res:
            out.append(res)
    return out


def track_for_id(track_id):
    """Get TrackInfo objects for a given ID string.
    """
    out = []
    for plugin in find_plugins():
        res = plugin.track_for_id(track_id)
        if res:
            out.append(res)
    return out


def template_funcs():
    """Get all the template functions declared by plugins as a
    dictionary.
    """
    funcs = {}
    for plugin in find_plugins():
        if plugin.template_funcs:
            funcs.update(plugin.template_funcs)
    return funcs


def import_stages():
    """Get a list of import stage functions defined by plugins."""
    stages = []
    for plugin in find_plugins():
        if hasattr(plugin, 'import_stages'):
            stages += plugin.import_stages
    return stages


# New-style (lazy) plugin-provided fields.

def item_field_getters():
    """Get a dictionary mapping field names to unary functions that
    compute the field's value.
    """
    funcs = {}
    for plugin in find_plugins():
        if plugin.template_fields:
            funcs.update(plugin.template_fields)
    return funcs


def album_field_getters():
    """As above, for album fields.
    """
    funcs = {}
    for plugin in find_plugins():
        if plugin.album_template_fields:
            funcs.update(plugin.album_template_fields)
    return funcs


# Event dispatch.

def event_handlers():
    """Find all event handlers from plugins as a dictionary mapping
    event names to sequences of callables.
    """
    all_handlers = defaultdict(list)
    for plugin in find_plugins():
        if plugin.listeners:
            for event, handlers in plugin.listeners.items():
                all_handlers[event] += handlers
    return all_handlers


def send(event, **arguments):
    """Sends an event to all assigned event listeners. Event is the
    name of  the event to send, all other named arguments go to the
    event handler(s).

    Returns a list of return values from the handlers.
    """
    log.debug(u'Sending event: {0}'.format(event))
    for handler in event_handlers()[event]:
        # Don't break legacy plugins if we want to pass more arguments
        argspec = inspect.getargspec(handler).args
        args = dict((k, v) for k, v in arguments.items() if k in argspec)
        handler(**args)
