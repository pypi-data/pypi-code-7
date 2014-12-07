class ShiftMemoryException(Exception):
    """
    Main memory exception category
    All package exceptions extend that to allow you to catch exception by
    component in a general way
    """
    pass


class ConfigurationException(ShiftMemoryException):
    """
    Configuration exception
    Gets raised when there's something wrong with your configs
    """
    pass

class AdapterMissingException(ShiftMemoryException):
    """
    Adapter missing exception
    Raised when you try to create a cache win nonexistent adapter
    """
    pass

class AdapterFeatureMissingException(ShiftMemoryException):
    """
    Adapter feature missing exception
    Raised when you you ask adapter to do something it can't. Like
    drop all caches or optimize
    """
    pass

class ValueException(ShiftMemoryException, ValueError):
    """
    Value exception
    Raised whenever we encounter an incorrect value
    """
    pass
