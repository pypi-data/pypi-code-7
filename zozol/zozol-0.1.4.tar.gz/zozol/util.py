from __future__ import print_function
from collections import namedtuple
import base64
import StringIO
import struct

Document = namedtuple('Document', ('label', 'body', 'headers'))

def u(data):
    return unicode(bytes(data), 'latin')


class LabelError(ValueError):
    pass


def to_pem(data, name):
    ret = StringIO.StringIO()
    ret.write('-----BEGIN {}-----\n'.format(name.upper()))
    for x in range(0, len(data), 48):
        ret.write(base64.b64encode(data[x:x+48]))
        ret.write('\n')
    ret.write('-----END {}-----\n'.format(name.upper()))
    return ret.getvalue()


def strip_header(data, off):
    section = off
    while data[off] and (off - section) < 20:
        off += 1

    off += 1
    label = u(data[section:off])
    (tlen,) = struct.unpack_from('<I', data, off)
    off += 4
    return label, off, tlen


def decode_hlist(hl, cp):
    return {
        str(k): unicode(str(v), cp)
        for k, v in hl
    }


def decode_headers(data):
    ret = []
    is_win = False
    for line in data.split('\r\n'):
        if '=' not in line:
            continue

        k, v = line.split('=', 1)
        ret.append((k, v))
        if k == 'ENCODING' and v == 'WIN':
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
        raise LabelError("Unknown label ".format(repr(label)))

    return Document(label=label[:-1], body=data[off:off+tlen], headers=headers)
