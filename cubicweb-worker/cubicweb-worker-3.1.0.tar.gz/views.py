# copyright 2011-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-worker views/forms/actions/components for web ui"""

from cwtags.tag import div, h3
from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance
from cubicweb.web.views.primary import PrimaryView

_ = unicode


class WorkerTask(PrimaryView):
    __select__ = is_instance('CWWorkerTask')

    def render_entity_attributes(self, entity):
        w = self.w
        super(WorkerTask, self).render_entity_attributes(entity)
        adapted = entity.cw_adapt_to('IWorkflowable')
        if adapted.state in ('task_pending', 'task_assigned'):
            self._cw.html_headers.add_raw(u'<meta http-equiv="Refresh" content="15; url=%s"/>\n' %
                                          xml_escape(entity.absolute_url()))

    def render_entity_relations(self, entity):
        if entity.reverse_handle_workertask:
            self.wview('primary', entity.reverse_handle_workertask[0].as_rset())
        super(WorkerTask, self).render_entity_relations(entity)

