"""Functions intended specifically for use as Jinja template filters."""


from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

from zlib import adler32

from jinja2 import evalcontextfilter, Markup

from .formatters import line_as_html


def colorhash(string):
    """Return an HTML color "hash" for *string*."""
    return '#{:03x}'.format(adler32(string.encode('utf-8')) & 0x777)


@evalcontextfilter
def ircformat(ctx, message):
    """Given a *message* containing mIRC formatting codes, return an
    HTML rendering."""
    html = line_as_html(message)
    if ctx.autoescape:
        return Markup(html)
    return html
