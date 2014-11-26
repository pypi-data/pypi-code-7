# copyright 2012-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-worker automatic tests"""
import time

from cubicweb import ValidationError

from cubicweb.devtools import testlib, PostgresApptestConfiguration

from cubes.worker.workutils import worker_pending_tasks
from cubes.worker.testutils import run_all_tasks

import threading

class SynchronisedRepo(object):
    repo = None

    def setUp(self):
        super(SynchronisedRepo, self).setUp()
        self.repo.cv = threading.Condition()
        self.repo._type_source_cache.clear()
        self.repo._extid_cache.clear()

    def tearDown(self):
        # We have to copy the list. because when a thread ens it remove itself
        # from the list altering the iteration
        for thread in list(self.repo._running_threads):
            thread.join()
        super(SynchronisedRepo, self).tearDown()


class DefaultTC(SynchronisedRepo, testlib.CubicWebTC):


    def test_bogus_operation(self):
        with self.admin_access.repo_cnx() as cnx:
            with self.assertRaises(ValidationError):
                cnx.create_entity('CWWorkerTask', operation=u'bogop')
                cnx.commit()

    def test_work_is_done(self):
        cv = self.repo.cv
        with self.admin_access.repo_cnx() as cnx:
            with cv:
                task_orig = cnx.create_entity('CWWorkerTask',
                                              operation=u'test_operation',
                                              test_val=0)
                cnx.commit()
                worker = cnx.execute('Any CWW WHERE CWW is CWWorker').get_entity(0,0)
                worker_pending_tasks(self.repo, {'eid': worker.eid})
                cv.wait(5)
                task = cnx.execute('Any CWWT WHERE CWWT eid %d' % task_orig.eid).get_entity(0,0)

            state = task.cw_adapt_to('IWorkflowable').state
            self.assertNotEqual('task_pending', state)
            self.assertEqual(task.test_val, task_orig.test_val + 1)

    def test_task_are_acquired(self):
        with self.admin_access.repo_cnx() as cnx:
            task1 = cnx.create_entity('CWWorkerTask',
                                      operation=u'no_op',
                                      test_val=0)
            task2 = cnx.create_entity('CWWorkerTask',
                                      operation=u'no_op',
                                      test_val=0)
            cnx.commit()
            worker = cnx.execute('Any CWW WHERE CWW is CWWorker').get_entity(0,0)
            cnx.commit()
            worker_pending_tasks(self.repo, {'eid': worker.eid})
            self.assertEqual(2, len(worker.reverse_done_by))

    def test_testutils(self):
        with self.admin_access.repo_cnx() as cnx:
            task1 = cnx.create_entity('CWWorkerTask',
                                      operation=u'test_operation',
                                      test_val=0)
            task2 = cnx.create_entity('CWWorkerTask',
                                      operation=u'test_operation',
                                      test_val=0)
            cnx.commit()
            tasks = run_all_tasks(cnx)
            cnx.commit()
            self.assertEqual(2, len(tasks))
            self.assertEqual([[1], [1]],
                             cnx.execute('Any V WHERE T is CWWorkerTask, T test_val V').rows)

    def test_load(self):
        with self.admin_access.repo_cnx() as cnx:
            task1 = cnx.create_entity('CWWorkerTask',
                                      operation=u'no_op',
                                      test_val=0)
            task2 = cnx.create_entity('CWWorkerTask',
                                      operation=u'no_op',
                                      test_val=0)
            cnx.commit()
            worker = cnx.execute('Any CWW WHERE CWW is CWWorker').get_entity(0,0)

            self.assertEqual(0, worker.get_load())

            worker.acquire_task(task1)
            cnx.commit()
            self.assertEqual(1, worker.get_load())

            worker.acquire_task(task2)
            cnx.commit()
            self.assertEqual(2, worker.get_load())

            worker.commit_transition(task2, 'task_complete', 'success')
            cnx.commit()
            self.assertEqual(1, worker.get_load())

            worker.commit_transition(task1, 'task_complete', 'success')
            cnx.commit()
            self.assertEqual(0, worker.get_load())

    def test_failure(self):
        with self.admin_access.repo_cnx() as cnx:
            cv = self.repo.cv
            with cv:
                task_orig = cnx.create_entity('CWWorkerTask',
                                              operation=u'fail_validation',
                                              test_val=0)
                cnx.commit()
                worker = cnx.execute('Any CWW WHERE CWW is CWWorker').get_entity(0,0)
                worker_pending_tasks(self.repo, {'eid': worker.eid})
                cv.wait(5)
                cnx.commit()
            task = cnx.execute('Any CWWT WHERE CWWT eid %d' % task_orig.eid).get_entity(0,0)
            task.cw_clear_all_caches()
            wfable = task.cw_adapt_to('IWorkflowable')
            self.assertEqual('task_failed', wfable.state)
            comment = wfable.latest_trinfo().comment
            self.assertEqual('error during validation', comment)


class PostgresWorkerTC(SynchronisedRepo, testlib.CubicWebTC):
    configcls = PostgresApptestConfiguration

    def test_subprocess_fail(self):
        """ test/data is not really an instance, hence
        launching cubicweb within the subprocess will fail.
        We nevertheless can test this failure and the workflow
        states.
        """
        self.repo.start_looping_tasks()
        start = time.time()
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('CWWorkerTask',
                              operation=u'test_operation',
                              use_subprocess=True,
                              test_val=0)
            cnx.commit()
            while (time.time() - start) < 30 :
                tstat = cnx.execute('Any S WHERE T is CWWorkerTask, T in_state ST, ST name S').rows
                sstat = cnx.execute('Any S WHERE T is Subprocess, T in_state ST, ST name S').rows
                if sstat and 'failed' in sstat[0][0]:
                    break
                time.sleep(1)
            self.assertEqual('task_failed', tstat[0][0])
            self.repo._tasks_manager.stop()


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
