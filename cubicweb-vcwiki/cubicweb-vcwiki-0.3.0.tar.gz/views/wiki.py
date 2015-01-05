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

"""cubicweb-vcwiki wiki display related views"""

from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance, score_entity
from cubicweb.tags import a, div
from cubicweb.uilib import cut
from cubicweb.web import stdmsgs
from cubicweb.web.formfields import StringField
from cubicweb.web.formwidgets import Button, SubmitButton, HiddenInput
from cubicweb.web.views.forms import FieldsForm
from cubicweb.web.views.baseviews import (InContextView, OneLineView,
                                          OutOfContextView)


from cubes.vcwiki import is_vcontent_of_wiki
from cubes.vcwiki.views import VCWikiView, has_write_perm_on_repo


class VCWikiViewPage(VCWikiView):
    """View page when the user cannot edit"""
    __regid__ = 'vcwiki.view_page'
    __select__ = VCWikiView.__select__ & ~has_write_perm_on_repo()
    consider_rev_parameter = True

    def empty_page_message(self):
        """Return the HTML snippet indicating that the page does not exist."""
        return self._cw._('This wiki page does not exist.')

    def page_title(self):
        if self.vcontent is not None:
            name = self.vcwiki.display_name(self.vcpage_path)
        else:
            name = self._cw._('New wiki page')
        return u'%s - %s' % (self.vcwiki.dc_title(), name)

    def entity_call(self, entity):
        if not self.vcontent:
            self.w(div(self.empty_page_message(), Class='stateMessage'))
        else:
            from logilab.mtconverter import TransformData
            from cubicweb.uilib import soup2xhtml
            from cubicweb.mttransforms import ENGINE
            context = self.vcwiki
            data = TransformData(self.vcontent, 'text/rest', 'utf-8', appobject=context)
            new_html_content = soup2xhtml(ENGINE.convert(data, 'text/html').decode(), 'utf-8')
            self.w(new_html_content)


class VCWikiViewPageCanEdit(VCWikiViewPage):
    """View page, when the user can edit"""
    __select__ = VCWikiView.__select__ & has_write_perm_on_repo()

    def empty_page_message(self):
        """Return the HTML snippet indicating that the page does not exist,
        with an invite link to create it.
        """
        basemsg = super(VCWikiViewPageCanEdit, self).empty_page_message()
        url = self.vcwiki.page_url(self._cw.form['wikipath'],
                                   vid='vcwiki.edit_page')
        link = a(self._cw._('Create this wiki page?'), href=xml_escape(url))
        return u' '.join([basemsg, link])


class VCWikiBaseItemViewMixIn(object):

    def cell_call(self, row, col, **kwargs):
        """Method used to override the default link target of the different one
        line views (oneline, incontext, outofcontext).
        """
        entity = self.cw_rset.get_entity(row, col)
        desc = cut(entity.dc_description(), 50)
        title = cut(entity.dc_title(),
                    self._cw.property_value('navigation.short-line-size'))
        self.w(u'<a href="%s" title="%s">%s</a>' % (
                xml_escape(entity.url), xml_escape(desc),
                xml_escape(title)))


class WikiOneLineView(VCWikiBaseItemViewMixIn, OneLineView):
    __select__ = OneLineView.__select__ & is_instance('VCWiki')


class WikiInContextView(VCWikiBaseItemViewMixIn, InContextView):
    __select__ = InContextView.__select__ & is_instance('VCWiki')


class WikiOutOfContextView(VCWikiBaseItemViewMixIn, OutOfContextView):
    __select__ = OutOfContextView.__select__ & is_instance('VCWiki')
