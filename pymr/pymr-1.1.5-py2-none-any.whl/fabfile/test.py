from fabric.api import local, task, execute


@task(default=True)
def all():
    """
    run flake8 and nosetests
    """
    execute(flake8)
    execute(unit_test)


@task()
def flake8():
    """
    run flake8
    """
    cmd = '. .pymrvenv/bin/activate && '
    cmd += 'flake8 --config .flake8rc *.py **/*.py --verbose'
    local(cmd)


@task()
def unit_test():
    """
    run nosetests
    """
    cmd = '. .pymrvenv/bin/activate && '
    cmd += 'nosetests --verbose'
    local(cmd)
