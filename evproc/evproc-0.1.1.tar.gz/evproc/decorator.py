# Copyright 2014 Rackspace
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the
#    License. You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing,
#    software distributed under the License is distributed on an "AS
#    IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#    express or implied. See the License for the specific language
#    governing permissions and limitations under the License.

import six


def want(*filters):
    """
    A decorator which may be used to indicate which events a given
    processor function will be called for.  Each argument may be
    either a string or a callable.  For strings, the event name must
    match one of the strings; for callables, each callable will be
    called with the event to be processed, and must return either a
    ``True`` or ``False`` value.  Only if the event name matches one
    of the strings (if any) *and* all of the callables (if any) return
    ``True`` will this filter match.

    This decorator may be used multiple times to establish an *OR*
    relationship; that is, if any of the filters declared with
    ``@want()`` match, then that processor function will be called
    with that event.

    :returns: A function decorator.
    """

    # First, sanity-check the arguments
    if not filters:
        raise TypeError("@want() takes at least 1 argument (0 given)")

    # Now, process them into a useable representation
    events = set()
    filt_funcs = []
    for filt in filters:
        if isinstance(filt, six.string_types):
            events.add(filt)
        elif callable(filt):
            filt_funcs.append(filt)
        else:
            raise TypeError("@want() must be called with strings or "
                            "callables, not %r" % filt)

    # Convert the events set into an appropriate filter
    if events:
        filt_funcs.insert(0, lambda ev: ev.name in events)

    # Set up the fulter function
    if len(filt_funcs) > 1:
        filt_func = lambda ev: all(filt(ev) for filt in filt_funcs)
    else:
        filt_func = filt_funcs[0]

    # The actual decorator function to return
    def decorator(func):
        filters = getattr(func, '_ev_filters', [])
        filters.insert(0, filt_func)
        func._ev_filters = filters
        return func

    return decorator


def requires(*procs):
    """
    A decorator which may be used to indicate that an event processor
    requires certain other event processors to have been run first.
    Each argument must be a string containing the name of the other
    event processor.  The decorator may be used multiple times, or it
    may be used once with all the event processor names passed in the
    argument list.

    :returns: A function decorator.
    """

    # First, sanity-check the arguments
    if not procs:
        raise TypeError("@requires() takes at least 1 argument (0 given)")

    # The actual decorator function to return
    def decorator(func):
        reqs = getattr(func, '_ev_requires', set())
        reqs |= set(procs)
        func._ev_requires = reqs
        return func

    return decorator


def required_by(*procs):
    """
    A decorator which may be used to indicate that an event processor
    will be required by certain other event processors.  This may be
    used to ensure that a given event processor runs before another
    event processor.  Each argument must be a string containing the
    name of the other event processor.  The decorator may be used
    multiple times, or it may be used once with all the event
    processor names passed in the argument list.

    :returns: A function decorator.
    """

    # First, sanity-check the arguments
    if not procs:
        raise TypeError("@required_by() takes at least 1 argument (0 given)")

    # The actual decorator function to return
    def decorator(func):
        reqs = getattr(func, '_ev_required_by', set())
        reqs |= set(procs)
        func._ev_required_by = reqs
        return func

    return decorator
