"""
Output syntax highlighting.
"""

import sys

from .config import config
from .logger import log

try:
    from pygments import highlight
    from pygments.lexer import RegexLexer, bygroups
    from pygments.token import Text, Generic
    from pygments.styles import STYLE_MAP

    from pygments.formatters import (NullFormatter,
                                     TerminalFormatter,
                                     Terminal256Formatter)

    class DitzLexer(RegexLexer):
        """
        Interactive Ditz lexer.
        """

        name = "Ditz"
        aliases = ['ditz', 'pyditz']

        tokens = {
            'root': [
                # Ditz prompt.
                (r'^Ditz:', Generic.Prompt),

                # Pager prompt.
                (r'^-- More .+$', Generic.Prompt),

                # Issue tag.
                (r'[a-z]+-\d+', Generic.Strong),

                # Feature indicator.
                (r'(?<=\()feature(?=\))', Generic.Inserted),

                # Bug indicators.
                (r'(?<=\()bug(?=\))', Generic.Deleted),
                (r'(?<=\* )bugfix(?=:)', Generic.Deleted),

                # Release lines.
                (r'^\d[^ \n]+(?= \()', Generic.Heading),
                (r'^Unassigned', Generic.Heading),

                # Closure indicators.
                (r'(?<=closed: )fixed', Generic.Inserted),
                (r'(?<=closed: )won\'t fix', Generic.Deleted),
                (r'(?<=closed: )reorganized', Generic.Strong),

                # Issue subheading.
                (r'^[A-Za-z ]{11}:', Generic.Subheading),

                # Email address.
                (r'[\w.]+@[\w.]+', Generic.Strong),

                # A 'changelog' title.
                (r'^(== +)([^ ]+)( +/ +)(.+)$',
                 bygroups(Text, Generic.Heading,
                          Text, Generic.Subheading)),

                # Error message.
                (r'^Error:', Generic.Error),

                # Everything else.
                (r'.', Text)
            ],
        }

    class DitzSessionLexer(RegexLexer):
        """
        Ditz output lexer.
        """

        name = "Ditz session"
        aliases = ['ditzsession']

        tokens = {
            'root': [
                # Special cases.
                (r'[_=>x] +[a-z]+-\d+: .+$', Text),
                (r'^( +Title|Description):.*$', Text),
                (r'^(Start|Stopp|Comment|Add|Chang|Clos)ing.+$', Text),

                # Prompt and response.
                (r'^([A-Z][^:?\n]*[:?])(.*)$',
                 bygroups(Text, Generic.Strong)),

                # User-typed comment.
                (r'^(>)(.*)$',
                 bygroups(Text, Generic.Strong)),

                # Everything else.
                (r'.*\n', Text)
            ],
        }

    enabled = config.getboolean('highlight', 'enable')
except ImportError:
    enabled = False


# Set up the terminal formatter.
if enabled:
    lexer = DitzLexer(encoding='utf-8', ensurenl=False)

    if sys.platform == 'win32':
        try:
            import colorama
            colorama.init()
            formatter = TerminalFormatter()
        except ImportError:
            formatter = NullFormatter()
    else:
        style = config.get('highlight', 'style')

        if style in STYLE_MAP:
            formatter = Terminal256Formatter()
        else:
            log.warning("'%s' is not a Pygments style" % style)
            formatter = NullFormatter()

    if not sys.stdout.isatty():
        formatter = NullFormatter()

    def colorize(text):
        return highlight(text, lexer, formatter)
else:
    def colorize(text):
        return text


def makeprompt(text):
    return colorize(text).strip() + " "
