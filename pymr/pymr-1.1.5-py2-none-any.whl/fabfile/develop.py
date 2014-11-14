from fabric.api import local, task, execute

import bootstrap
import test

__all__ = ['all']


@task(default=True)
def all():
    """
    bootstrap, test, and install from setup.py in develop mode
    """
    execute(bootstrap.all)
    execute(test.all)
    cmd = '. .pymrvenv/bin/activate && python setup.py develop'
    local(cmd)
