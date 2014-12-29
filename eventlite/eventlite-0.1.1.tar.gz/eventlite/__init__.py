"""
EventLite

Support for "light" event triggering from functions.

Example::

    import eventlite

    def handle_event(name):
        # do something
        pass

    with eventlite.handler(handle_event):
        eventlite.emit('foobar!')
"""

from eventlite.utils.local import LocalStack

_ctx_stack = LocalStack()


class EventHandler(object):
    def __init__(self, handler):
        self.handler = handler

    def push(self):
        _ctx_stack.push(self)

    def pop(self):
        rv = _ctx_stack.pop()
        assert rv is self, \
            'Popped wrong context: {0!r} instead of {1!r}'.format(rv, self)

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.pop()


# Shortcut :)
handler = EventHandler


def emit(*a, **kw):
    ctx = _ctx_stack.top
    if ctx is None:
        return
    ctx.handler(*a, **kw)
