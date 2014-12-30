import functools


def returns_boolean(func):
    """
    Method decorator that hints the collection class of
    an entity that the method returns a boolean.
    """
    func.returns_boolean = True
    return func


def entity_only(func):
    """
    Method decorator that hints the collection class of
    an entity that the method is entity only.
    """
    func.entity_only = True
    return func
