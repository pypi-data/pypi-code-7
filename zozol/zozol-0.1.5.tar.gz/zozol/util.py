from __future__ import print_function
import sys
from collections import namedtuple
import base64
try:
    import StringIO as io
except ImportError:
    import io
import struct

Document = namedtuple('Document', ('label', 'body', 'headers'))

if sys.version_info.major == 2:
    def u(data, cp='latin1'):
        return unicode(bytes(data), cp)
else:
    u = str


class LabelError(ValueError):
    pass


def to_pem(data, name):
    ret = io.StringIO()
    ret.write('-----BEGIN {}-----\n'.format(name.upper()))
    for x in range(0, len(data), 48):
        ret.write(u(base64.b64encode(data[x:x+48]), 'latin1'))
        ret.write('\n')
    ret.write('-----END {}-----\n'.format(name.upper()))
    return ret.getvalue()


def strip_header(data, off):
    section = off
    while data[off] and (off - section) < 20:
        off += 1

    off += 1
    label = u(data[section:off], 'latin1')
    (tlen,) = struct.unpack_from('<I', data, off)
    off += 4
    return label, off, tlen


def decode_hlist(hl, cp):
    return {
        u(k, 'latin1'): u(bytes(v), cp)
        for k, v in hl
    }


def decode_headers(data):
    ret = []
    is_win = False
    for line in data.split(b'\r\n'):
        if b'=' not in line:
            continue

        k, v = line.split(b'=', 1)
        ret.append((k, v))
        if k == b'ENCODING' and v == b'WIN':
            is_win = True

    return decode_hlist(ret, 'cp1251' if is_win else 'utf-8')


def decode_transport(data):
    if not isinstance(data, bytearray):
        data = bytearray(data)

    off = 0
    headers = {}
    label, off, tlen = strip_header(data, off)

    if label == 'TRANSPORTABLE\0':
        headers = decode_headers(data[off:off+tlen])
        label, off, tlen = strip_header(data, off + tlen)
    if label[3:] in ('_SIGN\0', '_CRYPT\0'):
        pass
    else:
        raise LabelError("Unknown label {}".format(repr(label)))

    return Document(label=label[:-1], body=data[off:off+tlen], headers=headers)
