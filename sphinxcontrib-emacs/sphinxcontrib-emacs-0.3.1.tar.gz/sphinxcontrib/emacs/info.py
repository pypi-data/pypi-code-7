# -*- coding: utf-8 -*-
# Copyright (c) 2014 Sebastian Wiesner <swiesner@lunaryorn.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Info manual support.
"""

import re
from string import Template

import requests
from docutils import nodes

from sphinxcontrib.emacs.util import normalize_space
from sphinxcontrib.emacs.nodes import infonode_reference


#: URL of the htmlxref database of GNU Texinfo
HTMLXREF_URL = 'http://ftp.hawo.stw.uni-erlangen.de/gnu/texinfo/htmlxref.cnf'

#: Regular expression object to parse the contents of an Info reference role.
INFO_RE = re.compile(r'\A\((?P<manual>[^)]+)\)(?P<node>.+)\Z')

HTMLXREF_RE = re.compile(r"""
^\s*
(?:
(?P<comment>[#].*) |
(?P<substname>\w+)\s*=\s*(?P<substurl>\S+) |
(?P<manname>\w+)\s*(?P<mantype>node|mono)\s*(?P<manurl>\S+)
)
\s*$
""", re.VERBOSE)


def node_encode(char):
    if char.isalnum():
        return char
    elif char == ' ':
        return '-'
    else:
        return '_00' + char.encode('hex')


def expand_node_name(node):
    """Expand ``node`` for use in HTML.

    ``node`` is the name of a node as string.

    Return a pair ``(filename, anchor)``, where ``filename`` is the base-name
    of the corresponding file, sans extension, and ``anchor`` the HTML anchor.

    See http://www.gnu.org/software/texinfo/manual/texinfo/html_node/HTML-Xref-Node-Name-Expansion.html.
    """
    if node == 'Top':
        return ('index', 'Top')
    else:
        normalized = normalize_space(node).encode('ascii', errors='ignore')
        encoded = ''.join(node_encode(c) for c in normalized)
        prefix = 'g_t' if not node[0].isalpha() else ''
        return (encoded, prefix + encoded)


class HTMLXRefDB(object):

    @classmethod
    def parse(cls, htmlxref):
        substitutions = {}
        manuals = {}
        for line in htmlxref.splitlines():
            match = HTMLXREF_RE.match(line)
            if match:
                if match.group('substname'):
                    url = Template(match.group('substurl')).substitute(
                        substitutions)
                    substitutions[match.group('substname')] = url
                elif match.group('manname') and match.group('mantype') == 'node':
                    url = Template(match.group('manurl')).substitute(
                        substitutions)
                    manuals[match.group('manname')] = url
        return cls(manuals)

    def __init__(self, entries):
        self.entries = entries

    def resolve(self, manual, node):
        manual_url = self.entries.get(manual)
        if not manual_url:
            return None
        else:
            filename, anchor = expand_node_name(node)
            return manual_url + filename + '.html#' + anchor


def update_htmlxref(app):
    if not isinstance(getattr(app.env, 'info_htmlxref', None), HTMLXRefDB):
        app.info('fetching Texinfo htmlxref database from {0}... '.format(
            HTMLXREF_URL))
        app.env.info_htmlxref = HTMLXRefDB.parse(
            requests.get(HTMLXREF_URL).text)
    app.env.info_htmlxref.entries.update(app.config.info_xref)


def resolve_info_references(app, _env, refnode, contnode):
    """Resolve Info references.

    Process all :class:`~sphinx.addnodes.pending_xref` nodes whose ``reftype``
    is ``infonode``.

    If the current output format is Texinfo, replace the
    :class:`~sphinx.addnodes.pending_xref` with a :class:`infonode_reference`
    node, which is then processed by the Texinfo writer.

    For all other output formats, replace the pending reference with a
    :class:`~docutils.nodes.reference` node, which references the corresponding
    web URL, as stored in the database referred to by :data:`HTMLXREF_URL`.

    """
    if refnode['reftype'] != 'infonode':
        return None

    target = normalize_space(refnode['reftarget'])
    match = INFO_RE.match(target)
    if not match:
        app.env.warn(refnode.source, 'Invalid info target: {0}'.format(target),
                     refnode.line)
        return contnode

    manual = match.group('manual')
    node = match.group('node')

    if app.builder.format == 'texinfo':
        reference = infonode_reference('', '')
        reference['refnode'] = node
        reference['refmanual'] = manual
        reference['has_explicit_title'] = refnode.get('has_explicit_title', False)
        reference.append(contnode)
        return reference
    else:
        xrefdb = app.env.info_htmlxref
        uri = xrefdb.resolve(manual, node)
        if not uri:
            message = 'Cannot resolve info manual {0}'.format(manual)
            app.env.warn(refnode.source, message, refnode.line)
            return contnode
        else:
            reference = nodes.reference('', '', internal=False,
                                        refuri=uri, reftitle=target)
            reference += contnode
            return reference
