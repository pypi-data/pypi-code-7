import json
import logging
from twisted.internet import protocol
from twisted.python import log

'''
    Handles all connections to clients.
    Clienthandler maintains connections with client and defines the client protocol

    To implement the protocol override connectionMade, connectionLost and lineReceived
'''
class JSONSocketProtocol(protocol.Protocol,):

    def __init__(self):
        self._buffer = ''
        self._wanted_length = None

    def sendData(self, data):
        """
        Sends a line to the other end of the connection.

        @param line: The line to send, not including the delimiter.
        @type line: C{bytes}
        """
        log.msg('JSONSocketProtocol', 'sendData', 'sending this data', data, logLevel=logging.DEBUG)
        try:
            j = json.dumps(data)
            return self.transport.write("%d#%s" % (len(j), j.encode("utf-8")))
        except:
            self.exceptionHandling()

    def dataReceived(self, data):

        try:
            log.msg('JSONSocketProtocol', 'dataReceived', data, logLevel=logging.DEBUG)
            self._buffer += data

            while "#" in self._buffer:
                head, tail = self._buffer.split("#", 1)
                if self._wanted_length is None:
                    self._wanted_length = int(head)

                if len(head) >= self._wanted_length:
                    message_data = json.loads(head[0:self._wanted_length])
                    self.lineReceived(message_data)

                    if len(head) > self._wanted_length:
                        self._wanted_length = int(head[self._wanted_length:])
                    else:
                        self._wanted_length = None

                self._buffer = tail

            if len(self._buffer) >= self._wanted_length:
                message_data = json.loads(self._buffer[0:self._wanted_length])
                self.lineReceived(message_data)
                self._buffer = self._buffer[self._wanted_length:]
                self._wanted_length = None

        except:
            self.exceptionHandling()

    def lineReceived(self, data):
        raise NotImplementedError('Subclass must implement lineReceived')

    def exceptionHandling (self):
        log.err()