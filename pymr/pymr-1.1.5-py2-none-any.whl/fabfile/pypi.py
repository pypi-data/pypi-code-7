from fabric.api import local, task


@task
def register():
    """
    register the project on pypi (original author only)
    """
    cmd = '. .pymrvenv/bin/activate && python setup.py register'
    local(cmd)


@task
def upload():
    """
    upload the project on pypi (original author only)
    """
    cmd = '. .pymrvenv/bin/activate && python setup.py bdist_wheel upload'
    local(cmd)
