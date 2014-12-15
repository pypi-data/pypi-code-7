# -*- coding: utf-8 -*-

__author__ = 'Thomas Bartelmess'
__email__ = 'tbartelmess@marketcircle.com'
__version__ = '0.1.7'

__all__ = ['Server']

import asyncio
from thrift.transport import TTransport
from thrift.transport.TTransport import TTransportBase
from struct import pack, unpack


class Protocol(asyncio.Protocol, TTransportBase):

    in_protocol = None
    out_protocol = None
    processor = None
    read_buffer = None
    write_buffer = None
    current_frame_size = None
    stream_writer = None

    def __init__(self, protocol_factory, processor):
        self.loop = asyncio.get_event_loop()
        self.in_protocol = protocol_factory.getProtocol(self)
        self.out_protocol = protocol_factory.getProtocol(self)
        self.processor = processor
        self.read_buffer = b''
        self.write_buffer = b''

    def data_received(self, data):
        self.read_buffer += data
        self.processor.process(self.in_protocol, self.out_protocol)

    def connection_made(self, transport):
        self.stream_writer = asyncio.StreamWriter(transport, self,
                                                  None,
                                                  self.loop)
        self.transport = transport
        loop = asyncio.get_event_loop()

    def open(self):
        pass

    def isOpen(self):
        return True

    def read(self, length):
        data = self.read_buffer[:length]
        if length >= len(self.read_buffer):
            self.read_buffer = b''
        else:
            self.read_buffer = self.read_buffer[length:]
        return data

    def write(self, data):
        self.stream_writer.write(data)

    def flush(self):
        yield from self.stream_writer.drain()


class Server(object):
    """
    Thrift Server using the Python asyncio module.
    """

    server_ready_event = None
    server_stop_event = None

    def __init__(self, host, port, protocol_factory, processor, ssl=None):
        self.host = host
        self.port = port
        self.protocol_factory = protocol_factory
        self.processor = processor
        self.ssl = ssl

    def make_protocol(self):
        return Protocol(self.protocol_factory, self.processor)

    def make_server(self, loop):
        return loop.create_server(self.make_protocol,
                                  host=self.host,
                                  port=self.port,
                                  ssl=self.ssl)

    def serve(self):
        loop = asyncio.get_event_loop()

        coro = self.make_server(loop)

        server = loop.run_until_complete(coro)
        if self.server_ready_event:
            self.server_ready_event.set()

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            loop.run_until_complete(server.wait_closed())
            if self.server_stop_event:
                self.server_stop_event.set()


class UnixServer(Server):
    def __init__(self, path, ssl=None):
        self.path = path
        self.ssl = ssl

    def make_server(self, loop):
        return loop.create_unix_server(self.make_protocol, path=self.path)

