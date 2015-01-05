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

from functools import partial

from logilab.mtconverter import xml_escape

from logilab.common.decorators import cachedproperty

from cubicweb.tags import a, div, input, span
from cubicweb.predicates import is_instance, match_form_params, score_entity
from cubicweb.web import stdmsgs
from cubicweb.web.form import Form
from cubicweb.web.formfields import StringField
from cubicweb.web.formwidgets import Button, SubmitButton, HiddenInput, Radio
from cubicweb.web.views.forms import FieldsForm
from cubicweb.web.views.formrenderers import HTableFormRenderer

from cubes.vcwiki.views import is_vcwiki_page, VCWikiView, has_write_perm_on_repo
from cubes.preview.views.forms import PreviewFormMixin


class VCWikiPageForm(PreviewFormMixin, FieldsForm):
    __abstract__ = True
    _default_form_action_path = 'vcwiki.edit_page'

    form_buttons = [SubmitButton(),
                    Button(stdmsgs.BUTTON_CANCEL, cwaction='cancel')]
    # Hidden fields
    vcwiki_eid = StringField('vcwiki_eid', widget=HiddenInput)
    path = StringField('wikipath', widget=HiddenInput)
    redirect = StringField('__redirectpath', widget=HiddenInput)
    # Commit message (visible) field
    message = StringField('message', label=_('commit message'))

    def redirect_path(self):
        return self.vcwiki.page_urlpath(unicode(self._cw.form['wikipath']))

    def __init__(self, *args, **kwargs):
        self.vcwiki = kwargs.pop('entity')
        self.vcontent = kwargs.pop('vcontent')
        super(VCWikiPageForm, self).__init__(*args, **kwargs)
        fbn = self.field_by_name
        fbn('vcwiki_eid').value = unicode(self.vcwiki.eid)
        fbn('wikipath').value = self.path
        fbn('__redirectpath').value = self.redirect_path()


class VCWikiEditPageView(VCWikiView):
    __regid__ = 'vcwiki.edit_page'
    __select__ = VCWikiView.__select__ & has_write_perm_on_repo()
    form_renderer_id = 'default'
    consider_rev_parameter = True

    @property
    def formid(self):
        """ Property used to help inheritance. """
        return self.__regid__

    def entity_call(self, entity):
        form = self._cw.vreg['forms'].select(
            self.formid, self._cw, form_renderer_id=self.form_renderer_id,
            entity=self.vcwiki, vcontent=self.vcontent)
        form.render(w=self.w)


class VCWikiEditPageForm(VCWikiPageForm):
    __regid__ = 'vcwiki.edit_page'
    __select__ = VCWikiPageForm.__select__ & has_write_perm_on_repo()

    @property
    def content_value(self):
        if self.vcontent is None:
            return u''
        return unicode(self.vcontent, 'utf-8')

    def __init__(self, *args, **kwargs):
        super(VCWikiEditPageForm, self).__init__(*args, **kwargs)
        field = StringField(_('content'), required=True,
                            value=self.content_value)
        self.fields.insert(0, field)


class VCWikiDeletePageView(VCWikiEditPageView):
    __regid__ = 'vcwiki.delete_page'
    __select__ = VCWikiEditPageView.__select__ & score_entity(is_vcwiki_page)


class VCWikiDeletePageForm(VCWikiPageForm):
    __regid__ = 'vcwiki.delete_page'
    content = StringField(_('content'), value=u'', widget=HiddenInput)

    def redirect_path(self):
        return self.vcwiki.urlpath


class VCWikiPageHistory(VCWikiView):
    __regid__ = 'vcwiki.page_history'
    __select__ = VCWikiView.__select__ & score_entity(is_vcwiki_page)

    @cachedproperty
    def revisions(self):
        return list(self.vcwiki.repository.cw_adapt_to('VCSRepo').log_rset(self.vcpage_path).entities())

    def page_title(self):
        return (self._cw._('%(vcwiki)s - History of %(wikipath)s')
                % {'vcwiki': self.vcwiki.dc_title(),
                   'wikipath': self._cw.form['wikipath'] or self._cw._('root index')})

    def intro(self):
        self.w(u'<div class="section"><h1>%s</h1>' % self.page_title())
        self.w(u'<p>%s</p>' % self._cw._('Choose two revisions in the form '
                                         'below to compare them.'))
        self.w(u'<p>%s</p>' % self._cw._('You may view the page as it was at a '
                                         'given revision by clicking on it.'))
        self.w(u'<p>%s</p>' % self._cw._('You may also revert the page content '
                                         'to its value using the revert link.'))
        self.w(u'</div>')

    def rev1_html(self, name='rev1', default_value=None, reverse_tags=False):
        html = []
        selected = self._cw.form.get(name) or default_value
        wikipath = self._cw.form['wikipath']
        for rev in self.revisions:
            a_content = rev.changeset or ('0' * 12)
            a_attrs = {'title': rev.description,
                       'href': self.vcwiki.page_url(wikipath, rev=rev.changeset)}
            i_attrs = {'name': name, 'type': 'radio', 'value': rev.changeset}
            if selected == rev.changeset:
                i_attrs['checked'] = 'checked'
            tags = [a(a_content, **a_attrs), input(**i_attrs)]
            if reverse_tags:
                tags.reverse()
            div_attrs = {}
            if rev.changeset == self.vcwiki.current_changeset():
                div_attrs['class'] = 'current'
            html.append(div(''.join(tags), **div_attrs))
        return ''.join(html)

    def rev2_html(self):
        return self.rev1_html('rev2', self.vcwiki.current_changeset(), True)

    def rev_date_html(self):
        fdate = partial(self._cw.format_date, time=True)
        return u''.join([div(fdate(rev.creation_date))
                         for rev in self.revisions])

    def rev_revert_html(self):
        html = []
        wikipath = self._cw.form['wikipath']
        for rev in self.revisions:
            div_content = u''
            if rev.eid != self.revisions[0].eid:
                msg = 'revert to revision %s' % rev.changeset
                href = self.vcwiki.page_url(wikipath, vid='vcwiki.edit_page',
                                            rev=rev.changeset, message=msg)
                a_content = self._cw._('Revert to revision %s') % rev.changeset
                div_content = a(a_content, href=href)
            html.append(div(div_content))
        return u''.join(html)

    def comparison_form(self):
        label = (self._cw._('Compare'), 'OK_ICON')
        button_html = SubmitButton(label=label).render(self)
        ctx = {'action': self.vcwiki.page_url(self._cw.form['wikipath']),
               'vid': xml_escape(self.__regid__),
               'rev1': self.rev1_html(),
               'rev2': self.rev2_html(),
               'date': self.rev_date_html(),
               'revert': self.rev_revert_html(),
               'h_rev1': xml_escape(self._cw._('Rev. 1')),
               'h_rev2': xml_escape(self._cw._('Rev. 2')),
               'h_date': xml_escape(self._cw._('Date')),
               'h_revert': xml_escape(self._cw._('Revert to an old rev.')),
               'button': button_html,
               }
        self.w(u'<form action="%(action)s" method="get">'
               u'<input type="hidden" name="vid" value="%(vid)s"/>'
               u'<table class="diff"><tbody>'
               u'<tr>'
               u'<th>%(h_rev1)s</th>'
               u'<th>%(h_rev2)s</th>'
               u'<th>%(h_date)s</th>'
               u'<th>%(h_revert)s</th>'
               u'</tr>'
               u'<tr>'
               u'<td class="rev1">%(rev1)s</td>'
               u'<td class="rev2">%(rev2)s</td>'
               u'<td class="date">%(date)s</td>'
               u'<td class="revert">%(revert)s</td>'
               u'</tr>'
               u'</tbody></table>'
               u'%(button)s'
               u'</form>' % ctx)

    def get_revision(self, repo, cs):
        return self._cw.execute(
            'Any R WHERE R changeset %(rev)s, R from_repository %(repo)s',
            {'repo': repo.eid, 'rev': cs}).get_entity(0, 0)

    def _write_msg(self, msg):
            self.w(u'<div class="stateMessage">%s</div>' % self._cw._(msg))

    def display_diff(self):
        form = self._cw.form
        if 'rev1' not in form or 'rev2' not in form:
            return
        repo = self.vcwiki.repository
        diff = None
        if repo.type == 'mercurial':
            rev1 = self.get_revision(repo, form['rev1'])
            rev2 = self.get_revision(repo, form['rev2'])
            diff = self._cw.call_service(
                'vcwiki.export-rev-diff', repo_eid=repo.eid,
                path=self.vcpage_path,
                rev1=rev1.changeset, rev2=rev2.changeset)
        self.w(u'<div class="section">')
        if diff is None:
            self._write_msg(_('Could not compute diff.'))
        elif diff == '':
            self._write_msg(_('Files are identical.'))
        else:
            self.w(u'<div class="content">')
            transformer = rev1._cw_mtc_transform
            html = transformer(diff, 'text/x-diff', 'text/annotated-html', 'utf8')
            self.w(html)
            self.w(u'</div>')
        self.w(u'</div>')

    def entity_call(self, entity):
        self.intro()
        self.comparison_form()
        self.display_diff()
