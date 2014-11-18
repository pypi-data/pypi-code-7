"""
Convenient functions for random terms generation.
"""
__all__ = ['rand_bytes', 'rand_uuid', 'rand_num', 'rand_int',
           'random', 'rand_num_range']

from _crypto import nacl_random as rand_bytes

from random import randint as rand_int, random, randrange as rand_range

from uuid import uuid4 as rand_uuid


def rand_num(size=4, sign=True, dec=True):
    i = int(rand_bytes(rand_int(1, size)).encode('hex'), 16)
    m = -1 if int(rand_bytes(1).encode('hex'), 16) % 2 else 1
    return m * i * ((1.0 + random()) if dec else 1)


def rand_num_range(size=4, step=1, sign=True):
    a, b = rand_num(size, dec=False), rand_num(size, dec=False)
    return rand_range(a, b, step=step)
