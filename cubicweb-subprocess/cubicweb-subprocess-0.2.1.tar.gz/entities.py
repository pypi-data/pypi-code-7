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

"""cubicweb-subprocess entity's classes"""

import os
import json
import signal
from subprocess import PIPE, Popen

from cubicweb import ValidationError, Binary
from cubicweb.entities import AnyEntity
from cubes.subprocess.error import ProcessNotRunning
from cubes.subprocess.utils import communicate


_ = unicode

def kill(pid):
    if os.name == 'posix':
        # no windows support for this before python 2.7 ...
        os.kill(pid, signal.SIGTERM)
    else:
        proc = Popen(['taskkill', '/f', '/pid', '%s' % pid])
        proc.wait()


class Subprocess(AnyEntity):
    __regid__ = 'Subprocess'
    envencoding = 'utf-8'

    def dc_title(self):
        try:
            return u' '.join(json.loads(self.cmdline))
        except (ValueError, TypeError):
            return self.cmdline

    @property
    def finished(self):
        '''Return True is the process has been run and finished.'''
        return not list(self.cw_adapt_to('IWorkflowable').possible_transitions())

    def _create_output_file(self, name):
        return self._cw.create_entity(
            'File',
            data=Binary(),
            data_format=u'text/plain',
            data_name=name,
            output_of=self,
        )

    def _environ(self):
        env = os.environ.copy()
        env.update(json.loads(self.env) if self.env else {})
        return dict((k.encode(self.envencoding) if isinstance(k, unicode) else k,
                     v.encode(self.envencoding) if isinstance(v, unicode) else v)
                    for k, v in env.iteritems())

    def _launch(self):
        """Launch a subprocess defined.

        The pid is stored in the db as soon as the subprocess is created,
        so that it can be used right away (for killing or status checking).

        Once terminated, the workflow transition is fired according to the
        return code of the subprocess.
        """
        cmd_args = json.loads(self.cmdline)
        proc = Popen(cmd_args, cwd=self.cwd,
                     env=self._environ(),
                     stdout=PIPE, stderr=PIPE)
        outputs = {'stdout': self._create_output_file(u'stdout'),
                   'stderr': self._create_output_file(u'stderr')}
        self.cw_set(pid=proc.pid)
        self._cw.commit(free_cnxset=False)

        for outname, content in communicate(proc):
            outputs[outname].data.write(content)
            outputs[outname].cw_set(data=outputs[outname].data)
            self._cw.commit(free_cnxset=False)

        return proc.wait()

    def _finalize(self, return_code, trname):
        """Save subprocess metadata into the database"""
        adapted = self.cw_adapt_to('IWorkflowable')
        if adapted.state == 'in progress':  # can be in other state if it
            adapted.fire_transition(trname) # was killed.
        self.cw_set(return_code=return_code)
        self._cw.commit()

    def _start(self):
        """Process the subprocess"""
        return_code = self._launch()
        trname = 'complete' if return_code == 0 else 'abort'
        self._finalize(return_code, trname)

    def start(self):
        """start the subprocess."""
        assert self.cw_adapt_to('IWorkflowable').state == 'in progress'
        def _launch():
            with self._cw.repo.internal_cnx() as cnx: # dedicated cnx in thread
                cnx.entity_from_eid(self.eid)._start()
        self._cw.repo.threaded_task(_launch)

    def synchronousstart(self):
        """start the subprocess."""
        session = self._cw
        wfadapter = self.cw_adapt_to('IWorkflowable')
        assert wfadapter.state == 'initialized'
        with session.allow_all_hooks_but('subprocess.workflow'):
            # this ^^ must be inhibited if we want control
            wfadapter.fire_transition('start', u'started synchronous subprocess')
            session.commit()
            session.set_cnxset()
        self.cw_clear_all_caches()
        return_code = self._start()
        return return_code

    def _kill(self):
        """kill the subprocess if it's running.
        """
        pid = self.pid
        if pid is None:
            raise ProcessNotRunning('The process is not started')
        kill(pid)

    def kill(self):
        """kill the subprocess if it is running."""
        if not self.cw_adapt_to('IWorkflowable').state == 'in progress':
            raise ValidationError(self.eid, {
                None: _('You must use the workflow to start the subprocess')})
        self._kill()
