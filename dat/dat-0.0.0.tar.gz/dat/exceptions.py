"""
This is where the exceptions live
"""


class MultipleObjectsExist(Exception):
    pass


class DoesNotExist(Exception):
    pass


class SerializationError(Exception):
    pass


class ValidationError(Exception):
    pass
