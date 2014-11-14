from fabric.api import local, task, execute


def delete_pyc():
    cmd = 'find . -name "*.pyc" -delete'
    local(cmd)


@task(default=True)
def all():
    """
    delete un-needed files (pyc)
    """
    delete_pyc()
