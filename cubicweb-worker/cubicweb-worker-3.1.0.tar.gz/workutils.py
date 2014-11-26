# copyright 2003-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb tag cube.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.

from logging import getLogger
from datetime import datetime, timedelta
from functools import partial

from cubicweb import ValidationError

logger = getLogger('cubicweb.worker')

def make_worker(cnx, repo):
    worker = cnx.execute('INSERT CWWorker W:  W last_ping %(last_ping)s',
                         {'last_ping': datetime.utcnow()}).get_entity(0, 0)
    return worker

def worker_ping(repo, eid_dict):
    with repo.internal_cnx() as cnx:
        try:
            worker = get_worker(cnx, repo, eid_dict)
        except ValueError:
            logger.warning('The worker %(eid)s apparently died.', eid_dict)
            worker = make_worker(cnx, repo)
            logger.warning('Recreating a new worker (%s)', worker.eid)
            eid_dict['eid'] = worker.eid
        else:
            cnx.execute('SET W last_ping %(tstamp)s WHERE W eid %(eid)s',
                        {'eid': eid_dict['eid'],
                         'tstamp': datetime.utcnow()})
        cnx.commit()

def worker_remove_stale_workers(repo, seconds=300):
    with repo.internal_cnx() as cnx:
        cnx.execute('DELETE CWWorker W  WHERE W last_ping < %(tstamp)s',
                    {'tstamp': datetime.utcnow() - timedelta(seconds=seconds)})
        cnx.commit()

def worker_remove_old_tasks(repo, hours=6):
    with repo.internal_cnx() as cnx:
        cnx.execute('DELETE CWWorkerTask W  WHERE W in_state S,'
                    'S name IN ("task_failed", "task_done"),'
                    'W modification_date < %(tstamp)s',
                    {'tstamp': datetime.now() - timedelta(hours=hours)})
        cnx.commit()

def get_worker(cnx, repo, eid_dict):
    try:
        # clear_caches is required because the worker may have been removed
        # by another instance, in which case we would get the cached entity.
        repo.clear_caches((eid_dict['eid'],))
        worker = cnx.execute('Any W WHERE W eid %(eid)s',
                             eid_dict).get_entity(0, 0)
    except IndexError:
        raise ValueError(eid_dict)
    return worker



def worker_pending_tasks(repo, eid_dict):
    task, worker = 0, None # None is used as a condition variable
    with repo.internal_cnx() as cnx:
        try:
            worker = get_worker(cnx, repo, eid_dict)
        except ValueError:
            logger.debug('worker_pending_tasks: no worker found, worker_ping will create a new one shortly')
            return

        while task is not None: # while there is job to do and the worker is not too loaded
            task = None
            try:
                task = worker.try_to_acquire_one_task()
                cnx.commit()
                # The work on the task itself must be done in another transaction / session
                if task is not None and worker is not None:
                    repo.threaded_task(partial(worker.perform_task, task))
            except ValidationError, exc:
                cnx.rollback()
            except Exception, exc: # IntegrityError: but this does look backend dependant
                if not exc.__class__.__name__ == 'IntegrityError':
                    # need string comparison because of various backends
                    raise # Not the Exception we are looking for. Keep moving.
                cnx.rollback()
                repo.warning('Commit fail: %s', exc)
                repo.warning('This may be due to two workers competing '
                             'for the same task (hence harmless).')


