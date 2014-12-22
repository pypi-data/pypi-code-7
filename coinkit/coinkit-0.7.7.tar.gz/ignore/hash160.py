# -*- coding: utf-8 -*-
"""
    Coinkit
    ~~~~~

    :copyright: (c) 2014 by Halfmoon Labs
    :license: MIT, see LICENSE for more details.
"""

import binascii, hashlib
from .formatcheck import is_hex

from .b58check import b58check_encode
from .errors import _errors

def bin_hash160(s):
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()

class Hash160():
    def __init__(self, public_key, version_byte=0):
        if is_hex(public_key):
            binary_public_key = binascii.unhexlify(public_key)
        else:
            binary_public_key = public_key
        self._binary_value = bin_hash160(binary_public_key)
        self._version_byte = version_byte
    
    def to_bin(self):
        return self._binary_value
    
    def to_hex(self):
        return binascii.hexlify(self.to_bin())
    
    def to_b58check(self):
        return b58check_encode(self.to_bin(), version_byte=self._version_byte)
    
    def address(self):
        return self.to_b58check()
    
    def __str__(self):
        return self.to_hex()

    def __repr__(self):
        return self.to_hex()

"""class PubkeyFormat():
    bin_ecdsa = 1
    hex_ecdsa = 2
    bin_uncompressed = 3
    hex_uncompressed = 4
    bin_compressed = 5
    hex_compressed = 6
"""

""" The address is the hash160 in b58check format. """

"""if hasattr(self, '_compressed_bin_public_key'):
    pubkey = self._compressed_bin_public_key
else:
    pubkey = self.to_bin()
"""
#return pubkey_to_address(pubkey, magicbyte=self._version_byte)

"""
# if the public key is compressed, decompress it
if is_hex(public_key) and len(public_key) == 66:
    public_key = decompress(public_key)
    self._compressed = True
elif len(public_key) == 33:
    public_key = decompress(public_key)
    self._compressed = True

# strip away the \x04 byte if it is present
if is_hex(public_key) and len(public_key) == 130 and public_key[0:2] == '04':
    public_key = public_key[2:]
elif len(public_key) == 65 and public_key[0] == '\x04':
    public_key = public_key[1:]

# get the binary version of the public key
if is_hex_ecdsa_pubkey(public_key):
    bin_public_key = unhexlify(public_key)
elif is_binary_ecdsa_pubkey(public_key):
    bin_public_key = public_key
else:
    raise ValueError(_errors['IMPROPER_PUBLIC_KEY_FORMAT'])
"""
