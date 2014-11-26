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

import sys
import time
import json
from contextlib import contextmanager

from cubicweb.devtools.testlib import CubicWebTC


@contextmanager
def saved_vars(obj):
    '''Save vars(obj) and restore it on exit.'''
    old_vars = vars(obj).copy()
    yield
    for key, value in old_vars.items():
        if not key.startswith('__'): # at least __doc__ is not writable
            setattr(obj, key, value)


class SubprocessTC(CubicWebTC):
    def pyprocess(self, cnx, pycode):
        '''Return a new subprocess executing the given python code (and commit
        without freeing the cnxset).
        The 'start' transition is silently fired (without hooks).
        '''
        cmdline = unicode(json.dumps([sys.executable, '-c', pycode]))
        subprocess = cnx.create_entity('Subprocess', cmdline=cmdline)
        cnx.commit(free_cnxset=False)
        return subprocess

    def wait_started(self, subprocess, max_duration=1):
        # wait until the subprocess is running
        starttime = time.time()
        while subprocess.pid is None:
            subprocess.cw_clear_all_caches()
            if (time.time() - starttime) > max_duration:
                self.fail('the process took more than %ss to start' %
                          max_duration)

    def wait_finished(self, subprocess, max_duration=1):
        '''Wait the ``subprocess`` to complete until ``max_duration`` (in
        seconds) is reached.
        '''
        starttime = time.time()
        while subprocess.return_code is None:
            subprocess.cw_clear_all_caches()
            if (time.time() - starttime) > max_duration:
                self.fail('the process took more than %ss to complete' %
                          max_duration)

    def _fire_transition(self, subprocess, trname):
        '''fire the transition ``trname`` on the ``subprocess`` (and commit
        without freeing the cnxset).
        '''
        subprocess.cw_adapt_to('IWorkflowable').fire_transition(trname)
        subprocess._cw.commit(free_cnxset=False)

    def fire_transition(self, subprocess, trname, deny_hooks=None):
        '''fire the transition ``trname`` on the ``subprocess`` (and commit
        without freeing the cnxset).
        '''
        if deny_hooks:
            with subprocess._cw.allow_all_hooks_but(deny_hooks):
                self._fire_transition(subprocess, trname)
                subprocess.cw_clear_all_caches()
        else:
            self._fire_transition(subprocess, trname)
