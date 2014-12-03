"""Test converter classes."""


class Bar(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, value, request, *args, **kwargs):
        return 'bar'
