import struct
from binascii import crc32
import six

import logging
logger = logging.getLogger(__name__)

_HEADER_SPEC = '!BHH'
_FOOTER_SPEC = '!I'
HEADER_LEN = struct.calcsize(_HEADER_SPEC)
FOOTER_LEN = struct.calcsize(_FOOTER_SPEC)

def _make_bytes(stri):
    if type(stri) != six.binary_type:
        return stri.encode('utf8')
    return stri

class Message (object):
    @classmethod
    def parse(cls, data, response):
        obj, _ = cls.parse_header(data[:HEADER_LEN], response)
        obj.parse_rest(data[HEADER_LEN:])
        return obj

    @classmethod
    def parse_header(cls, header, response):
        msgtype, id, length = struct.unpack(_HEADER_SPEC, header)

        if cls == Message:
            subcls = MESSAGE_CLASSES[msgtype]
        else:
            subcls = cls

        obj = subcls()
        obj.id = id
        obj.length = length
        obj.raw_header = header
        return obj, length + FOOTER_LEN

    def parse_rest(self, data):
        expected_crc = crc32(data[:-FOOTER_LEN], crc32(self.raw_header))
        (actual_crc,) = struct.unpack(_FOOTER_SPEC, data[-FOOTER_LEN:])
        # TODO: check CRCs
        logger.debug("header:%s body:%s crc:%s", repr(self.raw_header), repr(data)[:30], repr(actual_crc))
        self._parse_message_body(data[:-FOOTER_LEN])

    def encode(self, id):
        body = self._encode_message_body()
        header = struct.pack(_HEADER_SPEC, self.msgtype, id, len(body))
        raw_crc = crc32(body, crc32(header)) & 0xffffffff
        crc = struct.pack(_FOOTER_SPEC, raw_crc)
        logger.debug("header:%s body:%s crc:%s", repr(header), repr(body)[:30], repr(crc))
        return b''.join((header, body, crc))


class DirectoryListRequest (Message):
    msgtype = 0x01

    def __init__(self, path=[]):
        self.path = [_make_bytes(i) for i in path]

    def _parse_message_body(self, body):
        self.path = body.split(b'\0')

    def _encode_message_body(self):
        return b'\0'.join(self.path)

class DirectoryListResponse (Message):
    msgtype = 0x81

    def __init__(self, listing=[]):
        self.listing = listing

    def _parse_message_body(self, body):
        self.listing = body.split(b'\0')

    def _encode_message_body(self):
        return b'\0'.join(self.listing)

class NodeInfoRequest (Message):
    msgtype = 0x02

    def __init__(self, path=[]):
        self.path = [_make_bytes(i) for i in path]

    def _parse_message_body(self, body):
        self.path = body.split(b'\0')

    def _encode_message_body(self):
        return b'\0'.join(self.path)

class NodeInfoResponse (Message):
    msgtype = 0x82

    def __init__(self, isfile=False, size=0, created=0, accessed=0, modified=0):
        self.isfile = isfile
        self.size = size
        self.created = created
        self.accessed = accessed
        self.modified = modified

    def _parse_message_body(self, body):
        (self.isfile, self.size, self.created,
                self.accessed, self.modified) = struct.unpack('!?IIII', body)

    def _encode_message_body(self):
        return struct.pack('!?IIII', self.isfile, self.size,
                self.created, self.accessed, self.modified)

class FileContentsRequest (Message):
    msgtype = 0x03

    def __init__(self, offset=0, requested_length=0, path=[]):
        self.offset = offset
        self.requested_length = requested_length
        self.path = [_make_bytes(i) for i in path]

    def _parse_message_body(self, body):
        self.offset, self.requested_length = struct.unpack('!II', body[:8])
        self.path = body[8:].split(b'\0')

    def _encode_message_body(self):
        return (struct.pack('!II', self.offset, self.requested_length) +
                b'\0'.join(self.path))

class FileContentsResponse (Message):
    msgtype = 0x83

    def __init__(self, data=None):
        self.data = data

    def _parse_message_body(self, body):
        self.data = body

    def _encode_message_body(self):
        return self.data

class VersionRequest (Message):
    msgtype = 0x7F

    def _parse_message_body(self, body):
        pass

    def _encode_message_body(self):
        return b''

class VersionResponse (Message):
    """The Python representation of the version should be a 3-tuple: (major, minor, bugfix)"""
    msgtype = 0xFF

    def __init__(self, version=None):
        self.version = version

    def _parse_message_body(self, body):
        self.version = struct.unpack('!BBB', body)

    def _encode_message_body(self):
        return struct.pack('!BBB', *self.version)

class Error (Message):
    """The Python representation of the version should be a 3-tuple: (major, minor, bugfix)"""
    msgtype = 0x80

    def __init__(self, code=None):
        self.code = code

    def _parse_message_body(self, body):
        (self.code,) = struct.unpack('!B', body)

    def _encode_message_body(self):
        return struct.pack('!B', self.code)

    class Codes (object):
        DOES_NOT_EXIST = 0x01
        OTHER = 0xFF

MESSAGE_CLASSES = {
    0x01: DirectoryListRequest,
    0x02: NodeInfoRequest,
    0x03: FileContentsRequest,
    0x7F: VersionRequest,
    0x80: Error,
    0x81: DirectoryListResponse,
    0x82: NodeInfoResponse,
    0x83: FileContentsResponse,
    0xFF: VersionResponse,
}
