# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-vcwiki controllers"""

import json
from io import BytesIO
import mimetypes

from logilab.common.decorators import cachedproperty
from logilab.mtconverter import guess_mimetype_and_encoding, TransformData

from cubicweb import Binary
from cubicweb.uilib import soup2xhtml
from cubicweb.mttransforms import ENGINE
from cubicweb.predicates import is_instance, match_form_params
from cubicweb.web import Redirect, ValidationError
from cubicweb.web.views.basecontrollers import ViewController
from cubicweb.web.views.editcontroller import EditController

from cubes.preview.views.controllers import PreviewControllerMixin

from cubes.vcwiki.entities import split_path

class VCWikiViewController(ViewController):
    __regid__ = 'wiki'
    __select__ = ViewController.__select__ & match_form_params('wikiid', 'wikipath')

    def publish(self, rset=None):
        if self.vcwiki is None:
            self._cw.form['vid'] = 'noresult'
            return super(VCWikiViewController, self).publish()

        self.normalize_path()
        mimetype, vcontent = self.get_downloadable_content()
        if not mimetype.startswith('text/'):
            self._cw.set_content_type(mimetype)
            return vcontent
        self._cw.form.setdefault('vid', 'vcwiki.view_page')
        rset = self.vcwiki.as_rset()
        return super(VCWikiViewController, self).publish(rset)

    @cachedproperty
    def vcwiki(self):
        """ Return VCWiki instance designated by the URL or None."""
        rset = self._cw.execute('VCWiki W WHERE W name %(n)s',
                                {'n': self._cw.form.pop('wikiid')})
        if rset:
            return rset.get_entity(0, 0)

    def normalize_path(self):
        """ Normalize the web form's `path` parameter, handling the None case
        (== root path), and removing leading and trailing slashes, if any.
        """
        form = self._cw.form
        form['wikipath'] = (form['wikipath'] or u'').lstrip('/').rstrip('/')

    def get_downloadable_content(self):
        """ Return a boolean telling if the wiki content (if any) that matches
        the web form's wiki path `wikipath` is binary or not, and the
        matching VersionContent instance (or None if none match the given path).

        First try to get the content as a textual content, adding the vcwiki's
        content file extension to the web form given wiki path.

        If this fails (no content exists in the wiki's repository at this path)
        consider the path with no extension.
        """
        mimetype = 'text/'
        for vcfile_path in (self.vcwiki.vcpage_path(self._cw.form['wikipath']),
                            self._cw.form['wikipath']):
            vcontent = self.vcwiki.content(vcfile_path)
            if vcontent is not None:
                mimetype = mimetypes.guess_type(vcfile_path)[0]
                break
        return mimetype, vcontent


class VCWikiEditController(PreviewControllerMixin, EditController):
    __regid__ = 'vcwiki.edit_page'
    __select__ = match_form_params('vcwiki_eid', 'wikipath', 'content', 'message')

    def create_new_revision(self, vpath, content, msg):
        """ Create a new revision of the vcwiki with commit msg `msg`.
        If content is None, the versioned file with path `path` (if any) is
        deleted, otherwise its content is updated with `content`.
        When `content` if empty and the path points to a non yet existing file,
        an error is raised.
        """
        # handle the above-described error case
        if content is None and vpath not in self.vcwiki.repository.cw_adapt_to('VCSRepo').manifest(rev='tip'):
            raise ValidationError(self.vcwiki.eid, {'content': self._cw._(
                'can not set an empty content to a new wiki page')})
        if not content:
            added = ()
            deleted = (vpath,)
        else:
            content = content.encode('utf-8')
            added = ((vpath, BytesIO(content)),)
            deleted = ()
        # create the new revision
        author = self._cw.user.dc_title()
        if self._cw.user.primary_email:
            author += u' <%s>' % self._cw.user.primary_email[0].address
        new_rev = self.vcwiki.repository.make_revision(msg=msg.encode('utf-8'),
                author=author.encode('utf-8'), added=added, deleted=deleted, parentrev='tip')

    @cachedproperty
    def vcwiki(self):
        return self._cw.entity_from_eid(int(self._cw.form['vcwiki_eid']))

    def _default_publish(self):
        form = self._cw.form
        msg = form.get('message') or u'no commit message'
        vcfile_path = self.vcwiki.vcpage_path(form['wikipath'])
        self.create_new_revision(vcfile_path, form['content'], msg)

    def publish(self, rset=None):
        """ Use all EditController machinery but the HTTP Redirect response, to
        be transformed into a javascript redirect. """
        try:
            return super(VCWikiEditController, self).publish(rset)
        except Redirect as exc:
            return self._javascript_redirect(exc.location)
        except ValidationError as ex:
            return self._javascript_error(ex)

    def _javascript_redirect(self, url):
        """ Javascript redirect response from a child iframe. """
        return ('<script type="text/javascript">'
                'window.parent.location.replace(%s);'
                '</script>' % json.dumps(url))

    def _javascript_error(self, exception):
        self._cw.set_content_type('text/html')
        return """<script type="text/javascript">
 window.parent.handleFormValidationResponse('form', null, null, %s, null);
</script>""" % (json.dumps((False, (None, exception.errors), None)))

    def _action_preview(self):
        """ Preview machinery: publish as normal, but rollback and respond with
        the new, formatted, wiki page content. """
        self._default_publish()
        self._cw.cnx.rollback()
        form = self._cw.form
        # The new VersionContent is not available yet as the `at_revision`
        # relation to its revision is created in an Operation (after a commit).
        vcfile_path = self.vcwiki.vcpage_path(form['wikipath'])
        data = form['content'].encode(self._cw.encoding)
        format, encoding = guess_mimetype_and_encoding(
            encoding=self._cw.encoding, filename=vcfile_path, data=data)
        context = self.vcwiki
        data = TransformData(data, format, encoding, appobject=context)
        new_html_content = soup2xhtml(
            ENGINE.convert(data, 'text/html').decode(), encoding)
        domid = form.get('__domid', 'form')
        return self._preview_trampoline(domid, new_html_content, 'inline')
