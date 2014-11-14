from fabric.api import local, task


@task
def build():
    """
    create a new build of the docs
    """
    cmd = '. ./.pymrvenv/bin/activate && '
    cmd += 'mkdocs build'
    local(cmd)


@task
def serve():
    """
    start the mkdocs development server
    """
    cmd = '. ./.pymrvenv/bin/activate && '
    cmd += 'mkdocs serve'
    local(cmd)
