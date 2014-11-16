# -*- coding: utf-8 -*-
from jinja2 import nodes
from jinja2.ext import Extension
from datetime import date, datetime


class   DatetimeExtension(Extension):
    tags = set(['datetime'])

    def __init__(self, environment):
        super(DatetimeExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        args = [parser.parse_expression()]
        return nodes.CallBlock(
            self.call_method('_render', args),
            [], [], []).set_lineno(lineno)

    def _render(self, fmt, caller):
        return date.strftime(datetime.now(), fmt)
