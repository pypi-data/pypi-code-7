import socket
import serial
from .protocol import Message, HEADER_LEN

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

class MessageIO (object):
    def __init__(self, address):
        self.sock = open(address)
        self.counter = 0

    def _incr_counter(self):
        if self.counter >= 0xFFFF:
            self.counter = 0
        else:
            self.counter += 1

    def send_msg(self, message):
        self.sock.send(message.encode(self.counter))
        self._incr_counter()

    def _really_recv(self, count):
        # TODO: make this more efficient
        buf = b''
        while len(buf) < count:
            buf += self.sock.recv(count - len(buf))
        return buf

    def recv_msg(self):
        # TODO: make this more efficient
        head = self._really_recv(HEADER_LEN)
        obj, rest_len = Message.parse_header(head, response=True)
        rest = self._really_recv(rest_len)
        obj.parse_rest(rest)
        return obj

class SerialWrapper (object):
    """Wrapper for a PySerial serial connection that looks like a socket"""

    def __init__(self, ser):
        self.ser = ser

    def close(self):
        self.ser.close()

    def send(self, bytes):
        self.ser.write(bytes)

    def recv(self, buflength):
        return self.ser.read(buflength)

class NullDevice (object):
    """Socket-like object that does nothing"""

    def send(self, bytes):
        pass

    def recv(self, buflength):
        return ''

def open(address):
    """Opens a communication channel and returns a stream object that is
    guaranteed to have send(bytes) and recv(bufsize) methods.

    Example address values:

        unix:/tmp/virtualbox-sock
        serial:/dev/ttyS1
        serial:COM1
    """

    method, path = address.split(':', 1)

    if method == 'unix':
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(path)
        return sock

    if method == 'serial':
        ser = serial.Serial(path, 2400)
        return SerialWrapper(ser)

    if method == 'null':
        return NullDevice()

    raise ValueError('{} is not a valid method'.format(method))
