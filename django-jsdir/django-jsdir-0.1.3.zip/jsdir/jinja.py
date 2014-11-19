"""
Jinja2 extension to provide a {% jsdir %} tag
"""

from django.utils import six

from jinja2 import nodes
from jinja2.ext import Extension

from .core import JSDir


class JinjaTag(Extension):
    """
    Base class for a simple tag returning a constant string
    """

    tags = set(['jsdir'])

    def parse(self, parser):
        stream = parser.stream
        lineno = six.next(stream).lineno
        args = []
        kwargs = []

        while stream.current.type != 'block_end':

            if stream.current.type == 'name' and \
               stream.look().type == 'assign':
                key = nodes.Const(six.next(stream).value)
                stream.skip()
                value = parser.parse_expression()
                kwargs.append(nodes.Pair(key, value, lineno=value.lineno))
            else:
                args.append(parser.parse_expression())

        return nodes.Output([
            self.call_method('get_tags',
                             args=[nodes.List(args), nodes.Dict(kwargs)])
        ]).set_lineno(lineno)

    def get_tags(self, args, kwargs):
        try:
            path = args[0]
        except IndexError:
            raise ValueError('jsdir tag must have at least one argument')
        return JSDir(path, **kwargs).get_tags()


ext = JinjaTag
