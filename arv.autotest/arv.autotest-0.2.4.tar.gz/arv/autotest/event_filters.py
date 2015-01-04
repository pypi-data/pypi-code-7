# -*- coding: utf-8 -*-

# $Id$

"""This module defines some filters and filter factories.

A filter is any callable that receives a :py:class:`pyinotify.Event`
and returns a boolean value.

The :py:class:`~arv.autotest.main.EventHandler` class takes a filter as
argument in order to decide what events we are interested in.

"""

import time

import pyinotify

from arv.autotest import utils


def is_delete_dir_event(event):
    """Return ``True`` if deleting a directory.
    """
    P = pyinotify
    mask = event.mask
    return bool(
        (mask & P.IN_DELETE) and (mask & (P.IN_DELETE_SELF | P.IN_ISDIR))
        )


class simple_event_filter_factory(object):
    """Factory to create simple filters.

    Instances of this class behave as event filters.

    The constructor accepts a list of *watches*, each one defining how
    the filter should behave with regard to events triggered within a
    folder and its subfolders. Each watch has the properties defined
    by the :py:data:`~arv.autotest.config.WATCH_NODE_SCHEMA` schema.

    * a watch can be any object providing ``getattr``-like access to
      the properties.

    * a watch applied to a directory takes precedence over a watch
      applied to a parent directory.

    * exclusion rules are processed before inclusion rules.

    * additionally a ``global_ignores`` (a list of compiled regexs)
      can be specified to the constructor. That list takes precedence
      over all watches. This parameter is useful in gobally ignoring
      temporary files, VCS files etc.

    Instances of this class return ``True`` if the event is *included*
    according to the rules defined by the watches, ``False``
    otherwise.

    """
    def __init__(self, watches, global_ignores=[]):
        w = list(watches)
        # sort the watches by descending path length to make sure that
        # watches on subdirs are processed before its parents
        w.sort(key=lambda x : -len(x.path))
        self._watches = w
        self._global_ignores = global_ignores

    def __call__(self, event):
        return self._is_interesting(event.path, event.name)

    @utils.memoize
    def _is_interesting(self, path, name):
        if self._match_any(self._global_ignores, name):
            return False
        container = self._get_container(path)
        if container is None:
            # should never get here
            raise ValueError(path)
        if self._match_any(container.exclude, name):
            return False
        if self._match_any(container.include, name):
            return True
        return False

    def _get_container(self, path):
        for w in self._watches:
            if path.startswith(w.path):
                return w
        return None

    def _match_any(self, re_list, name):
        for r in re_list:
            if r.match(name):
                return True
        return False


class throttler_factory(object):
    """Throttling filter.

    This factory creates filters that discard events based on the
    number of events per second.

    The constructor expects an object with the attriutes:

    :max_events_second: integer, required. Determines the maximun
       number of events that the filter will accept in a second.

    Passing ``cfg=None`` to the constructor disables throttling and
    the filter accepts all events.

    """
    def __init__(self, cfg, timer=time.time):
        self._timer = timer
        if cfg:
            self._min_time = 1.0 / cfg.max_events_second
            self._last_time = None
            self._disabled = False
        else:
            self._disabled = True

    def adjust_delta(self, delta):
        # print "throttler.adjust_delta(%g)" % delta
        self._min_time = delta

    def __call__(self, event):
        if self._disabled:
            return True
        now = self._timer()
        if self._last_time is None:
            self._last_time = now
            return True
        if now - self._last_time < self._min_time:
            #print "throttling: drop event", self, event
            return False
        #print "throttling: accept event", self, event
        self._last_time = now
        return True

    def __str__(self):
        return "<throttler %5.3f %s>" % (self._min_time, self._last_time)


def and_(*filters):
    """Factory *anding* some filters together.
    """
    def filter(event):
        for f in filters:
            if not f(event):
                return False
        return True
    return filter

def not_(filter):
    """Factory *negating* a filter.
    """
    def f(event):
        return not filter(event)
    return f
