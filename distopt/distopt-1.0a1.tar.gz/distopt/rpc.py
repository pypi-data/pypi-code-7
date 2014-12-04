
import logging
import time
import zmq

from distopt import rpc_pb2

SECS_TO_MICROS = 1000000L

context = zmq.Context()

class RPC(object):
    pass

class RpcError(Exception):
    def __init__(self, status):
        self.status = status
    def __str__(self):
        return repr(self.status)

class Channel(object):
    def __init__(self, host, port):
        self.socket = context.socket(zmq.DEALER)
        self.socket.connect("tcp://%s:%s" % (host, port))

    def CallMethod(self, method, rpc, request, response_class, done):
        # TODO(mwytock): Make this threadsafe

        request_header = rpc_pb2.RequestHeader()
        request_header.rpc_id = long(time.time()*SECS_TO_MICROS)
        request_header.service = method.containing_service.name
        request_header.method = method.name

        self.socket.send(request_header.SerializeToString(), flags=zmq.SNDMORE)
        self.socket.send(request.SerializeToString())

        response_header = rpc_pb2.ResponseHeader.FromString(self.socket.recv())
        if response_header.status != rpc_pb2.ResponseHeader.OK:
            raise RpcError(response_header.status)
        return response_class.FromString(self.socket.recv())
