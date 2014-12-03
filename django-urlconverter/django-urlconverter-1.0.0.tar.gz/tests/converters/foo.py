"""Test converter classes."""


class Foo(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, value, request, *args, **kwargs):
        return 'foo'


class Converter(object):
    """Converter class that converts to itself.

    This object can be inspected in the tests to check how parameters are parsed.
    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, value, request, *args, **kwargs):
        return self
