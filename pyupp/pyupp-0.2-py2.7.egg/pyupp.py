"""
Read and write unity player preferences data with python

Implementation based on description of .upp files here:
http://answers.unity3d.com/questions/147431/how-can-i-view-a-webplayer-playerprefs-file.html

    File structure:

    16Byte header
    [Saved Prefs]
    for each saved pref:

    1 byte: length of pref name
    pref name
    1 byte type identifier
    [pref data] (depends on the type)
    That are the possible type identifier:

    0x00 - 0x7F is a short string that is smaller then 128 characters. The actual number is the length of the saved string.
    0x80 is a long string. The type identifier is followed by an additional 32Bit integer (4-byte little endian) length. After the length int you'll find the actual string.
    0xFD is an IEEE 32Bit float value(4 bytes).
    0xFE is a 32Bit integer (4-byte little endian).
    The header consists of the word "UnityPrf" (8 bytes) followed by (i guess) two version integers: 0x10000 and 0x100000
"""
from __future__ import print_function
from io import BytesIO

import binascii
import argparse
import logging
import six
import struct
import sys


def loads(data):
    """Parses `data` and returns a dictionary for the upp data"""
    reader = BytesIO(data)
    header = reader.read(16)
    assert header.startswith(b'UnityPrf')
    version = header[8:]
    _debug("version", version)

    result = {}
    while True:
        namelen = reader.read(1)
        _debug("namelen", namelen)

        # EOF
        if namelen == b'':
            break

        namelen = ord(namelen)
        name = reader.read(namelen).decode('UTF-8')
        _debug("name", name, True)
        assert name not in result
        valuetype = reader.read(1)
        _debug("valuetype", valuetype)
        if valuetype == b'\xfe':
            # 32-bit LE int
            packed = reader.read(4)
            _debug(name, packed)
            result[name] = _unpack_int(packed)
        elif valuetype == b'\xfd':
            # 32-bit LE float
            packed = reader.read(4)
            result[name] = _unpack_float(packed)
        elif valuetype == b'\x80':
            # long string
            packedlen = reader.read(4)
            strlen = _unpack_int(packedlen)
            value = reader.read(strlen)
            _debug(name, value, True)
            result[name] = value
        else:
            # short string?
            strlen = ord(valuetype)
            assert strlen <= 0x7f, repr((strlen, 0x7f))
            value = reader.read(strlen)
            _debug(name, value, True)
            result[name] = value

    return result


def dumps(data):
    """Serialized dictionary `data` to binary upp data"""
    writer = BytesIO()

    VERSION = b'\x00\x00\x01\x00\x00\x00\x10\x00'
    writer.write('UnityPrf'.encode('UTF-8'))
    writer.write(VERSION)
    for k, v in data.items():
        assert len(k) <= 255
        writer.write(_pack_ubyte(len(k)))
        writer.write(k.encode('UTF-8'))

        if isinstance(v, six.string_types) or isinstance(v, bytes):
            if len(v) <= 0x7f:
                writer.write(_pack_ubyte(len(v)))
                writer.write(v)
            else:
                writer.write(b'\x80')
                writer.write(_pack_int(len(v)))
                writer.write(v)

        elif isinstance(v, six.integer_types):
            writer.write(b'\xfe')
            writer.write(_pack_int(v))

        elif isinstance(v, float):
            writer.write(b'\xfd')
            writer.write(_pack_float(v))

        else:
            assert False, repr(('Unknown type of data:', v))
    return writer.getvalue()


def _debug(msg, dat, is_string = False):
    return
    if not is_string:
        logging.debug("%s (%d bytes) => %s",
            msg, len(dat), binascii.hexlify(dat))
    else:
        logging.debug("%s (%d bytes) => %s", msg,
            len(dat), repr(dat))


def _unpack_int(dat):
    assert len(dat) == 4
    result, = struct.unpack('<i', dat)
    return result


def _unpack_float(dat):
    assert len(dat) == 4
    result, = struct.unpack('<f', dat)
    return result


def _pack_int(n):
    assert n <= 0x7fffffff
    assert n >= -0x7fffffff
    assert isinstance(n, six.integer_types)
    return struct.pack('<i', n)


def _pack_ubyte(n):
    assert n <= 0xff
    assert n >= 0
    assert isinstance(n, six.integer_types)
    return struct.pack('<B', n)


def _pack_float(f):
    assert isinstance(f, float)
    return struct.pack('<f', f)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--check', action='store_true')
    ns = ap.parse_args()
    with open(ns.file, mode='rb') as f:
        dat = loads(f.read())
        print(dat)

    if ns.check:
        dumps(dat)
