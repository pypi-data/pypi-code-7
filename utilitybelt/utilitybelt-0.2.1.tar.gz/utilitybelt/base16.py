# -*- coding: utf-8 -*-
"""
    Utilitybelt
    ~~~~~

    :copyright: (c) 2014 by Halfmoon Labs
    :license: MIT, see LICENSE for more details.
"""

import string
from .charsets import change_charset

B16_CHARS = string.hexdigits[0:16]

def hexpad(x):
    return ('0' * (len(x) % 2)) + x

def charset_to_hex(s, original_charset):
    return hexpad(change_charset(s, original_charset, B16_CHARS))

def hex_to_int(s):
    try:
        return int(s, 16)
    except:
        raise ValueError("Value must be in hex format")

def int_to_hex(i):
    try:
        return hex(i).rstrip('L').lstrip('0x')
    except:
        raise ValueError("Value must be in int format")

def is_hex(s):
    # if there's a leading hex string indicator, strip it
    if s[0:2] == '0x':
        s = s[2:]
    # try to cast the string as an int
    try:
        i = hex_to_int(s)
    except ValueError:
        return False
    else:
        return True

def is_int(i):
    if isinstance(i, (int,long)):
        return True
    elif isinstance(i, str):
        try:
            int_i = int(i)
        except:
            return False
        else:
            return True
    else:
        return False
