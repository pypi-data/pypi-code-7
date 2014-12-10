

_record_type_registry = {}


def register_record(cls):
    """Decorator that add the client record class `cls` to the record type
       registry (as a constructor).
    """
    _record_type_registry[cls.RECTYPE] = cls
    return cls


def valid_rectype(rtype):
    """Is the record type registered with a constructor?
    """
    return rtype in _record_type_registry


def record_type(rtype):
    """Return the constructor for the record type.
    """
    return _record_type_registry[rtype]
