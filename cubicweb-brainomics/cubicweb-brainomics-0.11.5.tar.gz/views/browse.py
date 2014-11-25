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

from cubicweb.web import formfields as ff, Redirect, ValidationError
import cubicweb.web.formwidgets as fwdgs
from cubicweb.view import AnyRsetView
from cubicweb.web.views.basecontrollers import ViewController
from cubicweb.web.views import forms
from cubicweb.web.action import Action


###############################################################################
### BROWSER LIST ##############################################################
###############################################################################
BROWSABLE_ENTITIES = {'Subject': 'identifier'}


class BrainomicsBrowseEntityList(AnyRsetView):
    __regid__ = 'browse-list'

    def call(self):
        self.w(u'<div class="col-md-12">')
        self.w(u'<h2>%s</h2>' % self._cw._('Browse entities list'))
        self.w(u'<div class="well">%s</div>'
               % self._cw._('Browse for a list of entities using a CSV file. The CSV file should have '
                            'only one identifier by line.'))
        entities_form = self._cw.vreg['forms'].select('browse-list-form', self._cw)
        entities_form.render(w=self.w)
        self.w(u'</div>')


class BrainomicsBrowseEntityListForm(forms.FieldsForm):
    __regid__ = 'browse-list-form'
    form_buttons = [fwdgs.SubmitButton(label=_('Validate'), attrs={"class": "btn btn-primary"})]

    @property
    def action(self):
        return self._cw.build_url('browse-list-controller')

    filename = ff.FileField(name='__file',
                            label=_('Indentifiers file to import'),
                            order=1,)

    etype = ff.StringField(name='__etype',
                           label=_('Entity type'),
                           required=True,
                           help=_('Entity type'),
                           order = 2,
                           choices = BROWSABLE_ENTITIES.keys())


class BrainomicsBrowseEntityListController(ViewController):
    __regid__ = 'browse-list-controller'

    def _read_uuid_file(self, filename):
        try:
            fdesc = filename[1]
        except IOError as ioerr:
            raise ValidationError(None, 'File not found')
        else:
            uuids = ["'" + uuid.strip() + "'" for uuid in fdesc.readlines() if uuid.strip()]
        return uuids

    def publish(self, rset=None):
        filename = self._cw.form['__file']
        etype = self._cw.form['__etype']
        uuids = self._read_uuid_file(filename)
        if uuids:
            rql = ('Any X WHERE X is %(etype)s, X %(ident)s IN (%(uuids)s)'
                   % {'uuids': ', '.join(uuids), 'etype': etype,
                      'ident': BROWSABLE_ENTITIES[etype]})
            raise Redirect(self._cw.build_url(vid='list', rql=rql))
        raise Redirect(self._cw.base_url())


class BrainomicsBrowseEntityListAction(Action):
    __regid__ = 'browse-list-action'
    category = 'browse-links'
    title = _('Browse from list')

    def url(self):
        return self._cw.build_url(vid='browse-list')
