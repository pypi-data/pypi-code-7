""" perform.py is the subprocess wrapper that helps perform worker tasks """
import sys
import traceback as tb
import logging

from cubicweb.cwconfig import CubicWebConfiguration as cwcfg
from cubicweb.server.repository import Repository
from cubicweb.server.utils import TasksManager

# we want to log everythin to stdout
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def perform_task(repo, taskeid):
    with repo.internal_cnx() as cnx:
        task = cnx.entity_from_eid(taskeid)
        assert task.cw_adapt_to('IWorkflowable').state == 'task_assigned'
        performer = cnx.vreg['worker.performer'].select(task.operation, cnx, entity=task)
        try:
            performer.perform_task(cnx, task)
        except Exception, exc:
            task.cw_adapt_to('IWorkflowable').fire_transition('task_fail',
                                                              comment=unicode(tb.format_exc()))
        else:
            task.cw_adapt_to('IWorkflowable').fire_transition('task_complete')
        cnx.commit()

if __name__ == '__main__':
    import sys

    assert len(sys.argv) == 3
    appid, taskeid = sys.argv[1:]
    print appid, taskeid

    config = cwcfg.config_for(appid)
    config['connections-pool-size'] = 2
    config.bootstrap_cubes()
    config['long-transaction-worker'] = False
    config._cubes = None
    repo = Repository(config, TasksManager())
    perform_task(repo, taskeid)
