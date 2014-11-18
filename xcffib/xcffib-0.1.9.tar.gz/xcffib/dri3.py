import xcffib
import struct
import six
MAJOR_VERSION = 1
MINOR_VERSION = 0
key = xcffib.ExtensionKey("DRI3")
_events = {}
_errors = {}
from . import xproto
class QueryVersionReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.major_version, self.minor_version = unpacker.unpack("xx2x4xII")
        self.bufsize = unpacker.offset - base
class QueryVersionCookie(xcffib.Cookie):
    reply_type = QueryVersionReply
class OpenReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.nfd, = unpacker.unpack("xB2x4x24x")
        self.bufsize = unpacker.offset - base
class OpenCookie(xcffib.Cookie):
    reply_type = OpenReply
class BufferFromPixmapReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.nfd, self.size, self.width, self.height, self.stride, self.depth, self.bpp = unpacker.unpack("xB2x4xIHHHBB12x")
        self.bufsize = unpacker.offset - base
class BufferFromPixmapCookie(xcffib.Cookie):
    reply_type = BufferFromPixmapReply
class FDFromFenceReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.nfd, = unpacker.unpack("xB2x4x24x")
        self.bufsize = unpacker.offset - base
class FDFromFenceCookie(xcffib.Cookie):
    reply_type = FDFromFenceReply
class dri3Extension(xcffib.Extension):
    def QueryVersion(self, major_version, minor_version, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", major_version, minor_version))
        return self.send_request(0, buf, QueryVersionCookie, is_checked=is_checked)
    def Open(self, drawable, provider, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", drawable, provider))
        return self.send_request(1, buf, OpenCookie, is_checked=is_checked)
    def PixmapFromBuffer(self, pixmap, drawable, size, width, height, stride, depth, bpp, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIIHHHBB", pixmap, drawable, size, width, height, stride, depth, bpp))
        return self.send_request(2, buf, is_checked=is_checked)
    def BufferFromPixmap(self, pixmap, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", pixmap))
        return self.send_request(3, buf, BufferFromPixmapCookie, is_checked=is_checked)
    def FenceFromFD(self, drawable, fence, initially_triggered, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIB3x", drawable, fence, initially_triggered))
        return self.send_request(4, buf, is_checked=is_checked)
    def FDFromFence(self, drawable, fence, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", drawable, fence))
        return self.send_request(5, buf, FDFromFenceCookie, is_checked=is_checked)
xcffib._add_ext(key, dri3Extension, _events, _errors)
