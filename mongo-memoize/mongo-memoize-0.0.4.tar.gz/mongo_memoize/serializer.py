# -*- coding: utf-8 -*-

import base64
import cPickle as pickle


class NoopSerializer(object):
    """Serializer that does nothing.

    .. note::
        It is required that the result of the function can be stored
        directly in MongoDB when you use this serializer.
    """

    def serialize(self, obj):
        return obj

    def deserialize(self, serialized):
        return serialized


class PickleSerializer(object):
    """Serializer using Pickle.

    :param int protocol: Pickle protocol version.
    """
    def __init__(self, protocol=-1):
        self._protocol = protocol

    def serialize(self, obj):
        return base64.b64encode(pickle.dumps(obj, protocol=self._protocol))

    def deserialize(self, serialized):
        return pickle.loads(base64.b64decode(serialized))
