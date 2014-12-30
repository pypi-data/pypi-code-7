"""Interstat's core single-line and whole-file formatters."""


from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

from datetime import datetime
from itertools import tee
import re

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, PackageLoader
from jinja2.utils import urlize

# I'm mildly disgusted that the __name__ import works, but we need it
# later, so let's not look a gift horse in the mouth.
from . import __name__ as PACKAGE_NAME
from .formats import formats


#: A list of available message types.
MESSAGE_TYPES = ['privmsg', 'action', 'notice', 'nick', 'join',
                 'part', 'quit', 'kick', 'topic', 'mode']

#: A regex matching locations in an mIRC-formatted string where the
#: rendering may change.
FORMATTING_BOUNDARIES = re.compile(r"""
    \x02 |             # Bold
    \x03(?:            # Color
      ([0-9]{1,2})(?:  # Optional foreground number (from 0 or 00 to 99)
        ,([0-9]{1,2})  # Optional background number (from 0 or 00 to 99)
      )?
    )? |
    \x0F |             # Normal (revert to default formatting)
    \x16 |             # Reverse video (sometimes rendered as italics)
    \x1F |             # Underline
    ^ | $              # Beginning and end of string, for convenience
                       #   This *must* go at the end, otherwise it'll
                       #   take precedence over a control code at the
                       #   start of a string.
    """, re.VERBOSE)

#: A list mapping mIRC color codes (from 0 to 15) to CSS colors.
MIRC_COLORS = ['white', 'black', 'navy', 'green',
               'red', 'maroon', 'purple', 'olive',
               'yellow', 'lime', 'teal', 'cyan',
               'royalblue', 'pink', 'gray', 'lightgray']


def _pairwise(iterable):
    """Yield successive overlapping pairs from *iterable*."""
    a, b = tee(iterable)  # pylint: disable=invalid-name
    next(b, None)
    return zip(a, b)


def _toggle(mapping, key, value):
    """If *key* is set in *mapping*, delete its value.  Otherwise, set
    *key* to *value*."""
    if key in mapping:
        del mapping[key]
    else:
        mapping[key] = value


def mirc_color(numeric):
    """Return a CSS color corresponding to an mIRC color numeric."""
    try:
        numeric = int(numeric)
    except ValueError:
        numeric = 0
    # The modulo simulates the apparent behavior of a number of clients,
    # while handily eliminating out-of-bounds errors.
    return MIRC_COLORS[numeric % len(MIRC_COLORS)]


def line_as_html(message):
    """Given a *message* containing mIRC formatting codes, return an
    HTML rendering."""
    html = ''
    style = dict()
    matches = FORMATTING_BOUNDARIES.finditer(message)
    for first, second in _pairwise(matches):
        control_code = first.group(0)[:1]
        if control_code == '\x02':
            _toggle(style, 'font-weight', 'bold')
        elif control_code == '\x03':
            if first.group(1):
                style['color'] = mirc_color(first.group(1))
                if first.group(2):
                    style['background-color'] = mirc_color(first.group(2))
            else:
                style.pop('color', None)
                style.pop('background-color', None)
        elif control_code == '\x0F':
            style.clear()
        elif control_code == '\x16':
            _toggle(style, 'font-style', 'italic')
        elif control_code == '\x1F':
            _toggle(style, 'text-decoration', 'underline')

        text = urlize(message[first.end():second.start()])
        if text:  # Don't output empty <span> tags.
            if style:
                css = '; '.join('{}: {}'.format(k, v)
                                for k, v in sorted(style.items()))
                html += '<span style="{}">{}</span>'.format(css, text)
            else:
                html += text
    return html


def file_as_messages(log_file, format_name):
    """Yield message dicts from an IRC log file, parsed according to the
    given log format, suitable for passing into Interstat templates."""
    try:
        rules = formats[format_name]
    except KeyError:
        raise ValueError('unknown log format: {}'.format(format_name))
    for i, line in enumerate(log_file):
        match = rules['line'].match(line)
        if match is None:
            # Just don't bother with lines we can't get a timestamp for.
            continue
        message = {}
        message['id'] = 'L{}'.format(i + 1)
        message['timestamp'] = datetime.strptime(
            match.group('timestamp'), rules['timestamp'])
        line = match.group('line')
        for message_type in MESSAGE_TYPES:
            match = rules[message_type].match(line)
            if match is not None:
                message['type'] = message_type
                message.update(match.groupdict())
                break
        else:
            message['type'] = 'misc'
            message['content'] = line
        message['template'] = 'message/{}.html'.format(message['type'])
        yield message


def file_as_html(log_file, format_name, **kwargs):
    """Return an HTML rendering of an IRC log file, parsed according to
    the given log format."""
    kwargs['messages'] = file_as_messages(log_file, format_name)
    # Tell Jinja where to look for templates.
    loader_choices = [PackageLoader(PACKAGE_NAME)]
    if kwargs.get('template_dir'):
        template_dir = kwargs.pop('template_dir')
        loader_choices.insert(0, FileSystemLoader(template_dir))
    env = Environment(loader=ChoiceLoader(loader_choices),
                      keep_trailing_newline=True)
    # Import down here to avoid circularity issues.
    from .filters import colorhash, ircformat
    env.filters['colorhash'] = colorhash
    env.filters['ircformat'] = ircformat
    # pylint: disable=no-member
    return env.get_template('log.html').render(**kwargs)
