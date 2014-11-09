# -*- coding: utf-8 -*-

import cPickle as pickle
import hashlib


class PickleMD5KeyGenerator(object):
    """Cache key generator using Pickle and MD5.

    :param int protocol: Pickle protocol version.
    """

    def __init__(self, protocol=-1):
        self._protocol = protocol

    def __call__(self, args, kwargs):
        pickled_args = pickle.dumps((args, sorted(kwargs.iteritems())),
                               protocol=self._protocol)
        return hashlib.md5(pickled_args).hexdigest()
