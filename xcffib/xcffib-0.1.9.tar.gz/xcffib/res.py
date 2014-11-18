import xcffib
import struct
import six
MAJOR_VERSION = 1
MINOR_VERSION = 2
key = xcffib.ExtensionKey("X-Resource")
_events = {}
_errors = {}
from . import xproto
class Client(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.resource_base, self.resource_mask = unpacker.unpack("II")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=II", self.resource_base, self.resource_mask))
        return buf.getvalue()
    fixed_size = 8
class Type(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.resource_type, self.count = unpacker.unpack("II")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=II", self.resource_type, self.count))
        return buf.getvalue()
    fixed_size = 8
class ClientIdMask:
    ClientXID = 1 << 0
    LocalClientPID = 1 << 1
class ClientIdSpec(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.client, self.mask = unpacker.unpack("II")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=II", self.client, self.mask))
        return buf.getvalue()
    fixed_size = 8
class ClientIdValue(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.spec = ClientIdSpec(unpacker)
        self.length, = unpacker.unpack("I")
        unpacker.pad("I")
        self.value = xcffib.List(unpacker, "I", self.length)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=I", self.length))
        buf.write(self.spec.pack())
        buf.write(xcffib.pack_list(self.value, "I"))
        return buf.getvalue()
class ResourceIdSpec(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.resource, self.type = unpacker.unpack("II")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=II", self.resource, self.type))
        return buf.getvalue()
    fixed_size = 8
class ResourceSizeSpec(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.spec = ResourceIdSpec(unpacker)
        self.bytes, self.ref_count, self.use_count = unpacker.unpack("III")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=III", self.bytes, self.ref_count, self.use_count))
        buf.write(self.spec.pack())
        return buf.getvalue()
class ResourceSizeValue(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.size = ResourceSizeSpec(unpacker)
        self.num_cross_references, = unpacker.unpack("I")
        unpacker.pad(ResourceSizeSpec)
        self.cross_references = xcffib.List(unpacker, ResourceSizeSpec, self.num_cross_references)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=I", self.num_cross_references))
        buf.write(self.size.pack())
        buf.write(xcffib.pack_list(self.cross_references, ResourceSizeSpec))
        return buf.getvalue()
class QueryVersionReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.server_major, self.server_minor = unpacker.unpack("xx2x4xHH")
        self.bufsize = unpacker.offset - base
class QueryVersionCookie(xcffib.Cookie):
    reply_type = QueryVersionReply
class QueryClientsReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_clients, = unpacker.unpack("xx2x4xI20x")
        self.clients = xcffib.List(unpacker, Client, self.num_clients)
        self.bufsize = unpacker.offset - base
class QueryClientsCookie(xcffib.Cookie):
    reply_type = QueryClientsReply
class QueryClientResourcesReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_types, = unpacker.unpack("xx2x4xI20x")
        self.types = xcffib.List(unpacker, Type, self.num_types)
        self.bufsize = unpacker.offset - base
class QueryClientResourcesCookie(xcffib.Cookie):
    reply_type = QueryClientResourcesReply
class QueryClientPixmapBytesReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.bytes, self.bytes_overflow = unpacker.unpack("xx2x4xII")
        self.bufsize = unpacker.offset - base
class QueryClientPixmapBytesCookie(xcffib.Cookie):
    reply_type = QueryClientPixmapBytesReply
class QueryClientIdsReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_ids, = unpacker.unpack("xx2x4xI20x")
        self.ids = xcffib.List(unpacker, ClientIdValue, self.num_ids)
        self.bufsize = unpacker.offset - base
class QueryClientIdsCookie(xcffib.Cookie):
    reply_type = QueryClientIdsReply
class QueryResourceBytesReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_sizes, = unpacker.unpack("xx2x4xI20x")
        self.sizes = xcffib.List(unpacker, ResourceSizeValue, self.num_sizes)
        self.bufsize = unpacker.offset - base
class QueryResourceBytesCookie(xcffib.Cookie):
    reply_type = QueryResourceBytesReply
class resExtension(xcffib.Extension):
    def QueryVersion(self, client_major, client_minor, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2xB", client_major, client_minor))
        return self.send_request(0, buf, QueryVersionCookie, is_checked=is_checked)
    def QueryClients(self, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2x"))
        return self.send_request(1, buf, QueryClientsCookie, is_checked=is_checked)
    def QueryClientResources(self, xid, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", xid))
        return self.send_request(2, buf, QueryClientResourcesCookie, is_checked=is_checked)
    def QueryClientPixmapBytes(self, xid, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", xid))
        return self.send_request(3, buf, QueryClientPixmapBytesCookie, is_checked=is_checked)
    def QueryClientIds(self, num_specs, specs, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", num_specs))
        buf.write(xcffib.pack_list(specs, ClientIdSpec))
        return self.send_request(4, buf, QueryClientIdsCookie, is_checked=is_checked)
    def QueryResourceBytes(self, client, num_specs, specs, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", client, num_specs))
        buf.write(xcffib.pack_list(specs, ResourceIdSpec))
        return self.send_request(5, buf, QueryResourceBytesCookie, is_checked=is_checked)
xcffib._add_ext(key, resExtension, _events, _errors)
