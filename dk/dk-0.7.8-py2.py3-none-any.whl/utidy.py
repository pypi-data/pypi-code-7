# -*- coding: utf-8 -*-

"""Micro tidy.

   Usage::

       >>> print utidy('''
       ... <form name="FirmaForm" id="FirmaForm" method="POST" autocomplete="off"
       ... action="." class="fForm"><input type="hidden" name="__cmd"
       ... value="FirmaForm"></form>hello
       ... ''')
       ...
       <form action="." autocomplete="off" class="fForm" id="FirmaForm" method="POST" name="FirmaForm">
           <input name="__cmd" type="hidden" value="FirmaForm">
       </form>>
       hello

"""

import re

self_closing_tags = """
    area
    base
    br
    col
    command
    embed
    hr
    img
    input
    keygen
    link
    meta
    param
    source
    track
    wbr
""".split()


class HtmlTag(object):
    attre = re.compile(r"""
        (?P<attr>[-\w]+)                            # attribute
        (?:                                         # either = followed by..
           (?: = (?P<quote>['"])(.*?)(?P=quote))    #  something in quotes
          |(?: = ([^\s]+))                          #  something without quotes
        )?                                          # or a plain attribute
        """, re.VERBOSE)  # "

    def __init__(self, txt):
        self.orig = txt
        # collapse multiple spaces
        self.text = re.subn(r'(\s+)', " ", txt)[0]
        m = re.match(r'<\s*(/)?\s*([-\w]+)(\s.*)?>', self.text)
        if not m:
            print "NOT M:", txt
        g = m.groups()
        self.closing = g[0] is not None
        self.name = g[1]
        self.attrtxt = g[2] or ""
        self.selfclosing = self.name in self_closing_tags
        if not self.closing and self.attrtxt.strip():
            self.attrs = self.normalize_attrs(
                HtmlTag.attre.findall(self.attrtxt)
            )
        else:
            self.attrs = []
        self.kind = 'tag'
        if self.closing:
            self.kind += '-end'
        if not self.closing and not self.selfclosing:
            self.kind += '-start'

    def normalize_class(self, val):
        return ' '.join(sorted(val.split()))

    def normalize_style(self, val):
        return ';'.join(sorted([v for v in val.split(';') if v.strip()])) + ';'

    def normalize_attrs(self, attrs):
        res = []
        for attrname, _quote, qval, noqval in sorted(attrs):
            val = qval or noqval or attrname
            if attrname == 'class':
                res.append((attrname, self.normalize_class(val)))
            elif attrname == 'style':
                res.append((attrname, self.normalize_style(val)))
            else:
                res.append((attrname, val))
        return res

    def __str__(self):
        if self.closing:
            return "</%s>" % self.name
        res = "<%s" % self.name
        if self.attrtxt:
            res += ' '
        res += ' '.join(['%s="%s"' % (k, v) for k, v in self.attrs])
        res += ">"
        return res

    def __repr__(self):
        return "{{%s}}" % str(self)


def tokenize_html(html):
    tagre = re.compile(r'(<.*?>)', re.MULTILINE|re.DOTALL|re.UNICODE)
    tokens = []
    pos = 0
    while 1:
        m = tagre.search(html, pos)
        if not m:
            break

        txt = html[pos:m.start()]
        if txt.strip():
            tokens.append(('text', txt.strip()))

        tag = HtmlTag(html[m.start():m.end()])
        tokens.append((tag.kind, tag))

        pos = m.end()
    if pos < len(html):
        tokens.append(('text', html[pos:].strip()))
    return tokens


def utidy(html, level=0, indent='    '):
    """micro-tidy

       Normalizes the html.
    """
    tokens = tokenize_html(html.strip())
    res = []
    def _indent(n):
        return indent * max(0, n)
    i = level
    for kind, token in tokens:
        if kind == 'text':
            res.append(_indent(i) + token)
        elif kind == 'tag-start':
            res.append(_indent(i) + str(token))
            i += 1
        elif kind == 'tag-end':
            i -= 1
            res.append(_indent(i) + str(token))
        elif kind == 'tag':
            res.append(_indent(i) + str(token))
    return '\n'.join(res)


# print utidy('''
#     <div style="font-family:verdana;color:red" class="c b a">
#     <input type=checkbox data-toggle="#foo" checked>
#     </div>
#     ''')
