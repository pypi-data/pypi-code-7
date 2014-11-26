# -*- coding: utf-8 -*-
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-subprocess views/forms/actions/components for web ui"""

from logilab.mtconverter import BINARY_ENCODINGS, TransformError, xml_escape

from cubicweb.predicates import is_instance, adaptable
from cubicweb.web import component, httpcache
from cubicweb.web.views.baseviews import OutOfContextView
from cubicweb.web.views.idownloadable import DownloadBox
from cubicweb import tags


class SubprocessOutOfContextView(OutOfContextView):
    __select__ = OutOfContextView.__select__ & is_instance('Subprocess')

    def _progress_html(self, entity):
        return tags.tag('progress')(
            u'%.0f %%' % (100 * (entity.advance_ratio or 0)),
            value=entity.advance_ratio)

    def _link_html(self, entity):
        return self._cw.view('oneline', rset=entity.as_rset(), w=None)

    def _wrapper_html(self, entity, progress_html, link_html):
        div_classes = ['cw-subprocess-progress']
        adapted = entity.cw_adapt_to('IWorkflowable')
        state = adapted.state
        div_classes.append(state.replace(' ', '-'))
        if entity.finished:
            div_classes.append('ended')
        return tags.div(progress_html + link_html, Class=' '.join(div_classes),
                        title=state,
                        id=u'js-cw-subprocess-%s' % entity.eid)

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        if not entity.finished:
            self._cw.add_onload('cw.subprocess.autoRefreshImporter("%s");' % entity.eid)
        self.w(self._wrapper_html(entity,
                                  self._progress_html(entity),
                                  self._link_html(entity)))
