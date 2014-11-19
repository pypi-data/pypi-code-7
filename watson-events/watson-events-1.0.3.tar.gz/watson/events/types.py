# -*- coding: utf-8 -*-
from watson.common.imports import get_qualified_name


class Event(object):

    """A base event that can be subclassed for use with an EventDispatcher.

    Example:

    .. code-block:: python

        def my_listener(event):
            print(event.params['config'])

        dispatcher.add('MyEvent', my_listener)

        event = Event('MyEvent')
        event.params['config'] = {'some': 'config'}
        dispatcher.trigger(event)
    """
    name = None
    _stop_propagation = False
    params = None
    target = None

    def __init__(self, name, target=None, params=None):
        """Initializes the event.

        Initialize the Event based on an event name. The name will be used
        when the event is triggered from the event dispatcher.

        Args:
            name (string): the name of the event
            target (mixed): the originating target of the event
            params (dict): the params associated with the event
        """
        self.name = name
        self.target = target
        self.params = params or {}

    @property
    def stopped(self):
        """Return whether or not the event has been stopped.
        """
        return self._stop_propagation

    def stop_propagation(self):
        """Prevents the event from triggering any more event listeners.

        This should be used within an event listener when you wish to halt
        any further listeners from being triggered.
        """
        self._stop_propagation = True

    def __repr__(self):
        return '<{0} name:{1}>'.format(get_qualified_name(self), self.name)
