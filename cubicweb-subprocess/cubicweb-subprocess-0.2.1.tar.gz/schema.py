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

"""cubicweb-subprocess schema"""

from yams.buildobjs import String, Float, Int, RelationDefinition
from yams.constraints import IntervalBoundConstraint
from cubicweb.schema import WorkflowableEntityType


_ = unicode # pylint


class Subprocess(WorkflowableEntityType):
    cmdline = String(description=_('subprocess command line as a json list'), required=True)
    cwd = String(description=_('subprocess working directory [defaults to a temporary directory]'))
    env = String(description=_('subprocess environment variables as a json dict [defaults to application environment]'))
    pid = Int(description=_('subprocess system identifier'))
    advance_ratio = Float(description=_('Between 0 and 1'),
                          constraints=[IntervalBoundConstraint(minvalue=0, maxvalue=1)])
    return_code = Int(description=_('subprocess return code'))


class output_of(RelationDefinition):
    subject = 'File'
    object = 'Subprocess'
    cardinality = '?*'
    inlined = True
