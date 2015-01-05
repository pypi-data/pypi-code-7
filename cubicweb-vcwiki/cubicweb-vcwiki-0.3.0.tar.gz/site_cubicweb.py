import posixpath as posixp

from docutils import nodes, utils
from docutils.parsers.rst.roles import register_canonical_role, set_classes


def wiki_page_reference_role(role, rawtext, text, lineno, inliner,
                             options={}, content=[]):
    text = text.strip()
    try:
        wikipath, rest = text.split(u':', 1)
    except:
        wikipath, rest = text, text
    vcwiki = inliner.document.settings.context
    if 'wikipath' not in vcwiki._cw.form:
        return [nodes.Text(rest)], []
    my_path = vcwiki.vcpage_path(vcwiki._cw.form['wikipath'])
    # Allow users to link to a page with file extension
    ext = '.' + vcwiki.content_file_extension
    if wikipath.endswith(ext):
        wikipath = wikipath[:-len(ext)]
    # Return url and markup options
    if not wikipath.startswith('/'):
        vcpath = posixp.join(posixp.dirname(my_path), wikipath)
    else:
        vcpath = wikipath[1:]
    vcpath = posixp.normpath(vcpath)
    set_classes(options)
    if vcwiki.content(vcwiki.vcpage_path(vcpath)) is None:
        options['classes'] = ['doesnotexist']
    else:
        options.pop('classes', None)
    return [nodes.reference(rawtext, utils.unescape(rest),
                            refuri=vcwiki.page_url(vcpath),
                            **options)], []


register_canonical_role('wiki', wiki_page_reference_role)
