import json
import logging
from twisted.internet import protocol
from twisted.python import log


class JSONSocketProtocol(protocol.Protocol):
    """
    An implementation of the json socket protocol.

    Messages are in the format <len>#<json-payload>, which this protocol can
    handle the parsing and sending of.

    @see https://www.npmjs.org/package/json-socket
    """
    def __init__(self):
        self._buffer = ''
        self._wanted_length = None

    def sendData(self, data):
        """
        Sends a line to the other end of the connection.

        @param data: The data to send, will be encoded to json.
        @type line: C{dict}
        """
        log.msg('JSONSocketProtocol', 'sendData', 'sending this data', data, logLevel=logging.DEBUG)

        try:
            j = json.dumps(data)
            return self.transport.write("%d#%s" % (len(j), j.encode("utf-8")))
        except:
            self.exceptionHandling()

    def dataReceived(self, data):
        """
        Checks for any full length messages in the buffer, and calls
        lineReceived with the decoded data.
        """
        self._buffer += data
        part_length = 0

        # while there are messages, to be handled
        while "#" in self._buffer and len(self._buffer) >= part_length:
            head, tail = self._buffer.split("#", 1)

            msg_length = int(head)
            part_length = len(head) + 1 + msg_length

            # the tail contains enough data for the message, decode, handle and
            # strip it from the buffer
            if len(tail) >= msg_length:
                try:
                    data = json.loads(tail[0:msg_length].decode("utf-8"))

                    self.lineReceived(data)
                except ValueError:
                    self.exceptionHandling()
                finally:
                    self._buffer = self._buffer[part_length:]

    def exceptionHandling(self):
        log.err()

    def lineReceived(self, data):
        raise NotImplementedError('Subclass must implement lineReceived')
