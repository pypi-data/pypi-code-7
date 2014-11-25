# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2013 CEA (Saclay, FRANCE), all rights reserved.
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

"""cubicweb-brainomics views/forms/actions/components for web ui"""
from itertools import chain

from cubicweb.web.views.startup import IndexView


class BrainomicsIndexView(IndexView):

    def _display_panel(self, title, content, klass=u''):
        w = self.w
        w(u'<div class="panel %s">' % klass)
        w(u'<div class="panel-heading">')
        w(u'<h3 class="panel-title">%s</h3>' % title)
        w(u'</div>')
        w(u'<div class="panel-body">%s</div>' % content)
        w(u'</div>')

    def display_list_panel(self, items, title, content):
        html = []
        html.append(u'<p>%s</p>' % content)
        html.append(u'<ul class="list-unstyled">')
        for etype, rql, etitle in items:
            if rql is None:
                rql = 'WHERE X is %s' % etype
            rset = self._cw.execute('Any COUNT(X) %s' % rql)
            if not rset[0][0]:
                continue
            rset = self._cw.execute('Any X LIMIT 1 %s' % rql)
            view = self._cw.vreg['views'].select_or_none('outofcontext', self._cw, rset=rset)
            url = self._cw.build_url(rql='Any X %s' % rql, vid='sameetypelist')
            if etitle is None:
                etitle = self._cw._(etype)
            icon = (('<span class="glyphicon glyphicon-%s"></span>' % view.icon)
                    if hasattr(view, 'icon') and view.icon else u'')
            html.append(u'<li><a href="%s">%s %s</a></li>' % (url, icon, etitle))
        html.append(u'</ul>')
        self._display_panel(title, '\n'.join(html), 'panel-info')

    def display_infos(self):
        w = self.w
        rset = self._cw.execute('Any X WHERE X is Card, X wikiid %(t)s', {'t': 'index'})
        if not rset:
            return
        w(u'<div class="row"><div class="col-md-8">')
        w(u'<div class="jumbotron"><p>%s</p></div>'
          % rset.get_entity(0, 0).printable_value('content'))
        w(u'</div><div class="col-md-4">')
        if 'BIGLOGO' in self._cw.uiprops:
            w(u'<img id="biglogo" src="%s"/>' % self._cw.uiprops['BIGLOGO'])
        w(u'</div></div>')

    def display_dashboards(self):
        rset = self._cw.execute('Any X WHERE X is Card, X wikiid %(t)s', {'t': 'dashboards'})
        if not rset:
            return
        entity = rset.get_entity(0, 0)
        self._display_panel(entity.title, entity.printable_value('content'), 'panel-warning')

    def display_examples(self):
        rset = self._cw.execute('Any X WHERE X is Card, X wikiid %(t)s', {'t': 'rqlexamples'})
        if not rset:
            return
        entity = rset.get_entity(0, 0)
        self._display_panel(entity.title, entity.printable_value('content'), 'panel-warning')

    def get_clinical_data_etypes(self):
        measures = set([(r.type, None, None) for r in self._cw.vreg.schema.rschema('concerns').subjects()])
        return chain(((etype, None, None) for etype in ('Study', 'Subject', 'Therapy',
                      'Diagnostic', 'DrugTake')), measures)

    def get_thesaurus_data_etypes(self):
        return ((etype, None, None) for etype in ('Disease', 'BodyLocation', 'MedicalTechnique', 'Drug'))

    def call(self, **kwargs):
        w = self.w
        # Presentation
        w(u'<div class="page-header"><h1>%s</h1></div>' % self._cw.property_value('ui.site-title'))
        self.display_infos()
        # Panels
        w(u'<div class="col-md-12">')
        self.display_dashboards()
        w(u'</div>')
        # Patients
        w(u'<div class="col-md-6">')
        self.display_list_panel(self.get_clinical_data_etypes(),
                                self._cw._(u'Patient directory-based search'),
                                self._cw._('Access patient-related data'))
        w(u'</div>')
        # Vocabulaire
        w(u'<div class="col-md-6">')
        self.display_list_panel(self.get_thesaurus_data_etypes(),
                                self._cw._('Thesaurus-based search'),
                                self._cw._('Access thesaurus-based data for '
                                           'transversal retrieval'))
        w(u'</div>')
        # Examples
        self.display_examples()


def registration_callback(vreg):
    vreg.register_and_replace(BrainomicsIndexView, IndexView)
