from fabric.api import local, task


@task(default=True)
def all():
    """
    remove un-needed directories
    """
    cmd = 'rm -rf pymr.egg-info && '
    cmd += 'rm -rf dist && '
    cmd += 'rm -rf build'
    local(cmd)
