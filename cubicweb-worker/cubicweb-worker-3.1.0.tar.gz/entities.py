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
"""cubicweb-worker entity's classes"""
import socket
import sys
import os.path as osp
import json

from logging import getLogger
from warnings import warn

from logilab.common.registry import RegistrableObject, ObjectNotFound
from logilab.common.deprecation import class_renamed

from cubicweb import ValidationError, set_log_methods
from cubicweb.predicates import yes
from cubicweb.entities import AnyEntity, fetch_config

from cubes.subprocess.entities import Subprocess

import cubes.worker as workercube
from cubes.worker import Aborted
from cubes.worker.utils import UtilsHolder

_ = unicode




class SynchronousSubprocess(Subprocess):

    def dc_title(self):
        title = super(SynchronousSubprocess, self).dc_title()
        if not self.handle_workertask:
            return title
        return 'Subprocess for task %s ' % self.handle_workertask[0].dc_title()

    def synchronousstart(self):
        """start the subprocess."""
        cnx = self._cw
        wfadapter = self.cw_adapt_to('IWorkflowable')
        assert wfadapter.state == 'initialized'
        with cnx.allow_all_hooks_but('subprocess.workflow'):
            # this ^^ must be inhibited if we want control
            wfadapter.fire_transition('start', u'started synchronous subprocess')
            cnx.commit()
        self.cw_clear_all_caches()
        self._start()


class CWWorker(AnyEntity, UtilsHolder):
    __regid__ = 'CWWorker'
    fetch_attrs, cw_fetch_order = fetch_config(['last_ping'])
    rql_load = ('Any COUNT(T) WHERE T done_by X, T in_state S,'
                'S name IN ("task_pending", "task_assigned"), X eid %(e)s')

    def dc_title(self):
        return (u'%s (hostname: %s last seen: %s)' %
                (self.eid, socket.getfqdn(), self.last_ping))

    def get_load(self):
        """number of running or runnable tasks for this worker"""
        return self._cw.execute(self.rql_load, {'e': self.eid})[0][0]

    def try_to_acquire_one_task(self):
        """Consider pending tasks if the worker load is not too high

        The first pending task is grabbed by the worker which:
        * changes the Tasks's state (will raise ValidationError if another
          worker has raced for it)
        * sets the done_by relation on the task
        * increments the CWWorker's load

        No more than one task is acquired. The acquired task is
        returned or None. The later may happen when:

        * load is already too high.
        * no task are available.

        This function may raise Exception (IntegrityError, backend dependant)
        when multiple worker race for the same Task.

        XXX Exception handling will be inlined in the future"""
        load = self.get_load()
        if load >= self._cw.vreg.config['worker-max-load']:
            self.info('load too high (%s)', load)
            return None
        rset = self._cw.execute('Any T, AA ORDERBY AA WHERE T is CWWorkerTask,'
                                '                           T modification_date AA,'
                                '                           T in_state S,'
                                '                           S name %(state)s',
                                {'state': 'task_pending'})
        if not rset:
            self.debug('no pending tasks for %s', self.dc_title())
            return None
        task = rset.get_entity(0,0)
        self.acquire_task(task)
        return task

    def acquire_task(self, task):
        """Try to acquire a task

        * change state to "task_assigned"
        * set the "CWTask done_by CWWorker" relation

        This function may raise Exception (IntegrityError, backend dependant)
        when multiple worker Race for the same Task."""
        self.commit_transition(task, 'task_acquire', lenient=True) # should fail in case of a race condition
        task = self._cw.entity_from_eid(task.eid)
        task.cw_set(done_by=self)
        self.info('will process task %s', task.dc_long_title())

    def _handle_task_error(self, cnx, exc, task):
        """Handle exception raised by task processing

        /!\ This method is called by `perform_task` if error occurred     /!\
        /!\ during call to `do_<operation>` method. The initial exception /!\
        /!\ May be propagated using a bare `raise`                        /!\

        Do not forget to handle the generic cases or at least delegate them
        by a super call.

        _handle_task_error must return the created transition if any.
        """
        msg = None
        if isinstance(exc, ValidationError):
            self.info('Validation errors during task processing', exc_info=True)
            msg = 'error during validation'
        elif isinstance(exc, Aborted):
            self.info('%s aborted by user', task.dc_long_title())
            msg = 'aborted by user'
        else:
            self.exception('problem while processing task %s', task.dc_long_title())
            msg = 'unexpected : %s' % exc
        assert msg is not None
        return self.commit_transition(task, 'task_fail', msg)

    def perform_task(self, task):
        """Wrap the call to the actual task with workflow and error logic

        The task is performed within a dedicated temporary connection.
        """
        # this structure will be filled on a task call to abort_task
        # by the do_* method (the one that do actual work)
        with self.temp_cnx() as cnx:
            task = self.refresh(cnx, task)
            self.info('starting task %s', task.dc_long_title())
            # it is not necessary to raise the exceptions again:
            # we have done what we needed to do, and we're running
            # in a thread anyway, so noone's there to catch
            # them. It only generates spurious log entries in the
            # threading log file.
            subprocess = ()
            method = getattr(self, 'do_%s' % task.operation, None)
            if method:
                warn('[3.0.0] do_<operation> methods on the worker entity are deprecated. '
                     'Use a Worker adapter instead.',
                     DeprecationWarning)
            else:
                try:
                    performer = cnx.vreg['worker.performer'].select(task.operation,
                                                                    cnx,
                                                                    entity=task)
                except ObjectNotFound:
                    performer = task.cw_adapt_to(task.operation)
                    if performer is None:
                        self.warning('Bailing out: could not find adapter for %s', task.operation)
                        exc = Exception('no adapter for %s' % task.operation)
                        return self._handle_task_error(cnx, exc, task)
                method = performer.perform_task
                subprocess = task.use_subprocess
            try:
                # we give the session and forget about it
                # hence it may be in an unpredictable state
                # after the call, we should not touch it again ...
                if not subprocess:# or cnx.vreg.config.mode == 'test':
                    result = method(cnx, task)
                else:
                    # will do I/O bound thread watching
                    # => we can have quite a bit of these before suffering
                    # too much from GIL induced latency
                    result = self._launch_task_in_subprocess(cnx, task)
                    if result == 'failed':
                        raise Exception('The subprocess failed')
                    # the subprocess wrapper will handle the task transitions
                    # we're really done *here*
                    return
            except Exception, exc:
                # exception can be reraised by _handle_task_error
                return self._handle_task_error(cnx, exc, task)
            else:
                self.info('completed task %s: %s', task.dc_long_title(), result)
                return self.commit_transition(task, 'task_complete', result)

    def _launch_task_in_subprocess(self, cnx, task):
        cmdline = [sys.executable,
                   osp.join(osp.dirname(workercube.__file__), 'script', 'perform.py'),
                   cnx.vreg.config.appid,
                   str(task.eid)]
        proc = cnx.create_entity('Subprocess',
                                 handle_workertask=task,
                                 cmdline=unicode(json.dumps(cmdline)))
        cnx.commit()
        proc.synchronousstart()
        proc.cw_clear_all_caches()
        return proc.cw_adapt_to('IWorkflowable').state

class Performer(RegistrableObject):
    # the __regid__ will be transmitted as the operation of the workertask entity
    __registry__ = 'worker.performer'
    __regid__ = '<task.operation>'
    __select__ = yes()
    __abstract__ = True

    def __init__(self, cnx, entity=None):
        # this is to remain compatible with the previous
        # adapter-based implementation
        self._cw = cnx
        self.entity = entity

    def perform_task(self, cnx, task):
        """ real body/implementation of the task """
        raise NotImplementedError

WorkerAdapter = class_renamed('WorkerAdapter', Performer,
                              'The WorkerAdapter is replaced with Performer')


class CWWorkerTask(AnyEntity):
    __regid__ = 'CWWorkerTask'
    fetch_attrs, cw_fetch_order = fetch_config(['operation'])

    def __str__(self):
        state = self.cw_adapt_to('IWorkflowable').state
        return '%s %s' % (self.operation, state)

    def dc_title(self):
        return self.operation

    def dc_long_title(self):
        return u'WorkerTask %s %s' % (self.operation, self.dc_creator())


set_log_methods(CWWorker, getLogger('cubicweb.worker'))
set_log_methods(Performer, getLogger('cubicweb.worker'))
