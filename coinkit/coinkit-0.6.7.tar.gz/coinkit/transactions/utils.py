# -*- coding: utf-8 -*-
"""
    Coinkit
    ~~~~~

    :copyright: (c) 2014 by Halfmoon Labs
    :license: MIT, see LICENSE for more details.
"""

import struct
from binascii import hexlify, unhexlify
from utilitybelt import is_hex

UINT_MAX = 2**32-1

STANDARD_FEE = 1000 # 1000 satoshis = 10 bits = .01 mbits = .00001 BTC
OP_RETURN_FEE = 10000 # 10k satoshis = .0001 BTC
MAX_BYTES_AFTER_OP_RETURN = 40

def count_bytes(hex_s):
    """ Calculate the number of bytes of a given hex string.
    """
    assert(is_hex(hex_s))
    return len(hex_s)/2

def flip_endian(s):
    if is_hex:
        return hexlify(unhexlify(s)[::-1])
    return s[::-1]

def variable_length_int(i):
    """ Encodes integers into variable length integers, which are used in
        Bitcoin in order to save space.
    """
    if not isinstance(i, (int,long)):
        raise Exception('i must be an integer')

    if i < (2**8-3):
        return chr(i) # pack the integer into one byte
    elif i < (2**16):
        return chr(253) + struct.pack('<H', i) # pack into 2 bytes
    elif i < (2**32):
        return chr(254) + struct.pack('<I', i) # pack into 4 bytes
    elif i < (2**64):
        return chr(255) + struct.pack('<Q', i) # pack into 8 bites
    else:
        raise Exception('Integer cannot exceed 8 bytes in length.')