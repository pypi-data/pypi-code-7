# -*- coding: utf-8 -*-
"""
    sphinxcontrib.gravatar.nodes
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author: tell-k <ffk2005@gmail.com>
    :copyright: tell-k. All Rights Reserved.
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
    unicode_literals,
)
import os
import posixpath
import hashlib

from docutils import nodes

from sphinx.util.osutil import ensuredir
from sphinx.errors import SphinxError

from sphinxcontrib.gravatar.compat import urlopen, urlencode


class gravatar_image(nodes.General, nodes.Inline, nodes.Element):
    pass


class GravatarError(SphinxError):
    category = 'sphinxcontrib.gravatar error'


def _hash(email):
    """ Creating the hash for gravatar.

    :refs: https://en.gravatar.com/site/implement/hash/
    """
    return hashlib.md5(email.encode('utf-8')).hexdigest()


def build_gravatar_image_url(email, options):
    """ Build gravatar image url.

    :refs: https://en.gravatar.com/site/implement/images/
    """
    query_params = {}
    url = "http://www.gravatar.com/avatar/{0}".format(_hash(email))
    if options.get("size"):
        query_params.update({'s': options.get("size")})
    if options.get("default"):
        query_params.update({'d': options.get("default")})
    if options.get("force_default"):
        query_params.update({'f': 'y'})
    if options.get("rating"):
        query_params.update({'r': options.get("rating")})
    query = "?" + urlencode(query_params) if query_params else ''
    return url + query


def build_gravatar_profile_url(email):
    """ Build gravatar profile url.

    :refs: https://en.gravatar.com/site/implement/profile/
    """
    return "http://www.gravatar.com/{0}".format(_hash(email))


def get_image_filename(self, node, prefix='gravatar'):
    """ Get path of output file.  """

    opt = "-".join([str(v) for v in node["options"].values()])
    if opt:
        opt = "-" + opt

    fname = '{0}-{1}{2}.png'
    fname = fname.format(prefix, _hash(node['email']), opt)

    if hasattr(self.builder, 'imgpath'):
        # HTML
        relfn = posixpath.join(self.builder.imgpath, fname)
        outfn = os.path.join(self.builder.outdir, '_images', fname)
    else:
        # LaTeX
        relfn = fname
        outfn = os.path.join(self.builder.outdir, fname)

    if os.path.isfile(outfn):
        return relfn, outfn

    ensuredir(os.path.dirname(outfn))
    return relfn, outfn


def save_gravatar_image(outfn, node):
    """ Save gravatar image file to local.  """

    if not node['force_refresh'] and os.path.exists(outfn):
        return

    fd = urlopen(
        build_gravatar_image_url(node['email'], node['options'])
    )
    if not hasattr(fd, 'getcode') or fd.getcode() == 200:
        with open(outfn, 'wb') as fp:
            fp.write(fd.read())
    else:
        msg = "Can't fecth gravatar image for '{0}'"
        msg = msg.format(node['username'])
        raise GravatarError(msg)


def html_visit_gravatar_image(self, node):
    fname, outfn = get_image_filename(self, node)
    save_gravatar_image(outfn, node)

    linktag_format = '<a href="{0}" class="gravatar-link">{1}</a>'
    imgtag_format = '<img src="{0}" alt="{1}" class="{2}" />'

    imgtag = imgtag_format.format(fname, node['alt'], node['css_class'])

    if node['unlink']:
        self.body.append(imgtag)
    else:
        self.body.append(linktag_format.format(
            node['target'] or build_gravatar_profile_url(node['email']),
            imgtag,
        ))
    raise nodes.SkipNode


def latex_visit_gravatar_image(self, node):
    fname, outfn = get_image_filename(self, node)
    save_gravatar_image(outfn, node)
    if fname is not None:
        self.body.append('\\includegraphics{%s}' % fname)
    raise nodes.SkipNode
