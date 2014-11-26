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


from logilab.common.decorators import monkeypatch

from cubes.subprocess.entities import Subprocess

from utils import SubprocessTC, saved_vars


class WorkflowHooksTC(SubprocessTC):
    def test_start(self):
        with saved_vars(Subprocess):
            @monkeypatch(Subprocess)
            def start(self):
                self.cw_set(pid=1)

            with self.admin_access.client_cnx() as cnx:
                subprocess = self.pyprocess(cnx, 'print "toto"')
                self.fire_transition(subprocess, 'start')
                self.assertEqual(1, subprocess.pid)

    def test_kill(self):
        with saved_vars(Subprocess):
            @monkeypatch(Subprocess)
            def start(self):
                self.cw_set(pid=1)

            @monkeypatch(Subprocess)
            def kill(self):
                self.cw_set(pid=0)

            with self.admin_access.client_cnx() as cnx:
                subprocess = self.pyprocess(cnx, 'print "toto"')
                self.fire_transition(subprocess, 'start')
                self.fire_transition(subprocess, 'kill')
                self.assertEqual(0, subprocess.pid)



if __name__ == '__main__':
    import unittest
    unittest.main()
