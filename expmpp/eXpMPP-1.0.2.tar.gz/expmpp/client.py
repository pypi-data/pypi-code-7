#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import wraps
import xmpp


class NetworkError(IOError):
    pass


class AuthenticationError(NetworkError):
    pass


class Client(object):
    """XMPP notification client

    jid : str
        Jabber ID (JID) for the message-emitting account

    pwd : str
        Password for the message-emitting account

    listeners : iterable of str
        Jabber IDs (JIDs) that should receive notifications
        [Default: ()]
    """

    def __init__(self, jid, pwd, listeners=()):
        self.jid = jid = xmpp.protocol.JID(jid)
        self.client = client = xmpp.Client(jid.getDomain(), debug=())
        if not client.connect():
            raise NetworkError('could not connect')

        if not client.auth(jid.getNode(), pwd, resource=jid.getResource()):
            raise AuthenticationError('could not authenticate user')

        client.sendInitPresence()
        self._visible = True

        self.listeners = set(listeners)

    def __del__(self):
        self.client.disconnect()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, val):
        for listener in self.listeners:
            self.client.sendPresence(listener, val)
        self._visible = val

    def addListener(self, listener):
        """Add a listener.

        listener : str
            Jabber ID (JID)
        """
        self.listeners.add(listener)

    def removeListener(self, listener):
        """Remove a listener.

        listener : str
            Jabber ID (JID)
        """
        self.listeners.remove(listener)

    def _send(self, to, msg):
        self.client.send(xmpp.protocol.Message(to, msg))

    def notify(self, msg):
        """Send a notification to all registered listeners.

        msg : str
            Message to send to each listener
        """
        for listener in self.listeners:
            self._send(listener, msg)

    def monitor(self, msg, transformer=lambda _: _, unpack=False):
        """Decorator that sends a notification to all listeners when the
        wrapped function returns, optionally reporting said function's return
        value(s).

        msg : str
            Message to send to all listeners.  If the message is a
            Python-formatted string, the wrapped function's return value will
            be inserted into the first positional placeholder (i.e. `{0}`).

        transformer : function
            Function to format the wrapped function's return value for
            insertion into the `msg` parameter.  NOTE: this does *not* modify
            the function's ultimate return value.  Instead, it changes what is
            inserted into the message.
            [Default: lambda _: _]

        unpack : bool
            If true, multiple return values will be unpacked and each element
            will be inserted in the corresponding placeholder of `msg`.  For
            ordered collections, insertion is done via positional placeholders.
            If the return-value is a `dict`, insertion is performed via keyword
            placeholders.
            [Default: False]
        """
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kw):
                results = fn(*args, **kw)
                transformed = transformer(results)
                if unpack:
                    if isinstance(results, dict):
                        self.notify(msg.format(**transformed))
                    else:
                        self.notify(msg.format(*transformed))
                else:
                    self.notify(msg.format(transformed))
                return results
            return wrapper
        return decorator
