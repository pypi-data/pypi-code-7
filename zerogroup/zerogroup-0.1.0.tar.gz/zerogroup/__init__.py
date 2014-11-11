#!/usr/bin/env python

"""
ZeroMQ socket group wrapper.
"""

from .version import __version__

import re
import threading as th

# Non-standard serialization support not mandatory:
try:
    import msgpack
except:
    pass

import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream

def istransport(t):
    """
    Return True of `t` is a valid ZeroMQ transport.
    """

    try:
        status = bool(re.match('^(inproc|ipc|tcp|pgm|epgm)\://.*', t))
    except:
        return False
    else:
        return status

class ZeroGroup(object):
    """
    ZeroMQ socket group wrapper.

    Encapsulates a group of ZeroMQ sockets (and associated streams)
    sharing the same context and (for those sockets with streams) event loop.

    Parameters
    ----------
    context : zmq.Context
        ZeroMQ context to use. If no context is specified, a
        new one is created.
    ioloop : zmq.eventloop.ioloop.ZMQIOLoop
        IOLoop instance to use for event streams. If no instance is specified,
        a new one is created.

    Example
    -------
    >>> import zmq
    >>> g = SocketGroup()
    >>> g.add(zmq.DEALER, 'ipc://data', True, {zmq.IDENTITY: 'xyz'}, 'data')
    >>> g.add(zmq.DEALER, 'ipc://ctrl', True, {zmq.IDENTITY: 'xyz'}, 'ctrl')
    >>> g.create()
    >>> msg = g.recv('data')
    >>> g.send('ctrl', 'foo')
    """

    def __init__(self, context=None, ioloop=None):
        if context is None:
            self.context = zmq.Context()
        elif isinstance(context, zmq.Context):
            self.context = context
        else:
            raise ValueError('invalid context')
        if ioloop is None:
            self.ioloop = IOLoop.instance()
        elif isinstance(ioloop, IOLoop):
            self.ioloop = ioloop
        else:
            raise ValueError('invalid ioloop')

        self._created = False

        # Specifications of sockets to create:
        self.specs = {}

        # Maps addresses to sockets:
        self.sock = {}

        # Maps addresses to streams:
        self.stream = {}

        # Maps string aliases to addresses:
        self.alias = {}

    def _getaddr(self, n):
        """
        Convert alias to address.
        """

        if n in self.alias:
            return self.alias[n]
        elif n in self.sock:
            return n
        else:
            raise ValueError('unknown alias/address')

    def add(self, socket_type, addr, binding, 
            opts={}, alias=None, stream=False):
        """
        Add a new socket to the group.
        """

        if not istransport(addr):
            raise ValueError('invalid address')
        if alias and istransport(alias):
            raise ValueError('can only alias non-address to address')
        if not isinstance(opts, dict):
            raise ValueError('invalid options')
        self.specs[addr] = {'socket_type': socket_type,
                            'binding': binding,
                            'stream': stream,
                            'alias': alias,
                            'opts': opts}

    def create(self):
        """
        Create all specified sockets and streams.
        """

        if self._created:
            return
        for addr in self.specs:
            spec = self.specs[addr]
            sock = self.context.socket(spec['socket_type'])

            # Set socket options before binding:
            for opt, val in spec['opts'].iteritems():
                sock.setsockopt(opt, val)
            if spec['binding']:
                sock.bind(addr)
            else:
                sock.connect(addr)

            if spec['stream']:
                stream = ZMQStream(sock, self.ioloop)
                self.stream[addr] = stream
            else:
                stream = None

            self.sock[addr] = sock
            alias = spec['alias']
            if alias:
                self.alias[alias] = addr

                # Insert alias into self.stream so that it can be used to lookup 
                # a stream directly via self.stream[alias]:
                self.stream[alias] = addr
        self._created = True

    def poll(self, n, timeout=None, flags=1):
        """
        Poll socket for events.
        """

        return self.sock[self._getaddr(n)].poll(timeout, flags)

    def poll_in(self, n, timeout=None):
        """
        Poll socket for incoming events.
        """

        return self.sock[self._getaddr(n)].poll(timeout, zmq.POLLIN)

    def poll_out(self, n, timeout=None):
        """
        Poll socket for outgoing events.
        """

        return self.sock[self._getaddr(n)].poll(timeout, zmq.POLLOUT)

    def poll_all(self, n, timeout=None):
        """
        Poll socket for all events.
        """

        return self.sock[self._getaddr(n)].poll(timeout, zmq.POLLIN|zmq.POLLOUT)

    def send(self, n, data, flags=0, copy=True, track=False):
        """
        Send a message.
        """

        return self.sock[self._getaddr(n)].send(data, flags, copy, track)

    def send_multipart(self, n, msg_parts, flags=0, copy=True, track=False):
        """
        Send a multipart message.
        """

        return self.sock[self._getaddr(n)].send_multipart(msg_parts, flags, copy, track)

    def send_pyobj(self, n, obj, flags=0, protocol=-1):
        """
        Send a Python object as a message using pickle to serialize.
        """

        return self.sock[self._getaddr(n)].send_pyobj(obj, flags, protocol)

    def send_msgpack(self, n, obj, flags=0):
        """
        Send a Python object as a message using msgpack to serialize.
        """

        msg = msgpack.dumps(obj)
        return self.send(n, msg, flags)

    def recv(self, n, flags=0, copy=True, track=False):
        """
        Receive a message.
        """
        return self.sock[self._getaddr(n)].recv(flags, copy, track)

    def recv_multipart(self, n, flags=0, copy=True, track=False):
        """
        Receive a multipart message.
        """
        return self.sock[self._getaddr(n)].recv_multipart(flags, copy, track)

    def recv_pyobj(self, n, flags=0):
        """
        Receive a Python object serialized with pickle.
        """

        return self.sock[self._getaddr(n)].recv_pyobj(flags)

    def recv_msgpack(self, n, flags=0):
        """
        Receive a Python object serialized with msgpack.
        """

        s = self.sock[self._getaddr(n)].recv(flags)
        return msgpack.loads(s)

    def flush(self, n, flags=3, limit=None):
        """
        Flush stream.
        """

        return self.stream[self._getaddr(n)].flush(flags, limit)

    def on_recv(self, n, callback, copy=True):
        """
        Set stream receive handler.
        """

        self.stream[self._getaddr(n)].on_recv(callback, copy)

    def on_send(self, n, callback):
        """
        Set stream send handler.
        """

        self.stream[self._getaddr(n)].on_send(callback)

    def start_loop(self, threaded=False):
        """
        Start event loop.

        Parameters
        ----------
        threaded : bool
            If True, start the loop in a new thread.
        """

        if threaded:
            th.Thread(target=self.ioloop.start).start()
        else:
            self.ioloop.start()

    def stop_loop(self, flush=False, stop_on_recv=False, stop_on_send=False):
        """
        Stop event loop.

        Parameters
        ----------
        flush : bool
            Flush all streams before stopping the loop.
        stop_on_recv, stop_on_send : bool
            Run each stream's stop_on_recv() or stop_on_send() methods
            before stopping the loop.
        """

        for stream in self.stream.values():
            if flush:
                stream.flush()
            if stop_on_recv:
                stream.stop_on_recv()
            if stop_on_send:
                stream.stop_on_send()
        self.ioloop.stop()

    def __getitem__(self, n):
        return self.sock[self._getaddr(n)]

    def __iter__(self):
        for addr in self.sock.keys():
            yield addr
