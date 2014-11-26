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

def define_subprocess_workflow(add_workflow):

    wf = add_workflow(u'Subprocess workflow', 'Subprocess')
    initialized = wf.add_state(_('initialized'), initial=True)
    in_progress = wf.add_state(_('in progress'))
    succeeded = wf.add_state(_('succeeded'))
    failed = wf.add_state(_('failed'))
    killed = wf.add_state(_('killed'))

    wf.add_transition(_('start'), (initialized, ), in_progress, ('managers', 'owners'))
    wf.add_transition(_('complete'), (in_progress, ), succeeded, ())
    wf.add_transition(_('abort'), (in_progress, ), failed, ())
    wf.add_transition(_('kill'), (in_progress, ), killed, ('managers', 'owners'))
