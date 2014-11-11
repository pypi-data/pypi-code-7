#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import wraps
import xmpp


class NetworkError(IOError):
    pass


class AuthenticationError(NetworkError):
    pass


class Client(object):
    def __init__(self, jid, pwd, listeners=()):
        self.jid = jid = xmpp.protocol.JID(jid)
        self.client = client = xmpp.Client(jid.getDomain(), debug=())
        if not client.connect():
            raise NetworkError('could not connect')

        if not client.auth(jid.getNode(), pwd, resource=jid.getResource()):
            raise AuthenticationError('could not authenticate')

        client.sendInitPresence()
        self._visible = True

        self.listeners = listeners

    def __del__(self):
        self.client.disconnect()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, val):
        for listener in self.listeners:
            self.client.sendPresence(listener, True)
        self._visible = val

    def _send(self, to, msg):
        self.client.send(xmpp.protocol.Message(to, msg))

    def notify(self, msg):
        for listener in self.listeners:
            self._send(listener, msg)

    def monitor(self, msg, transformer=lambda _: _, unpack=False):
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
