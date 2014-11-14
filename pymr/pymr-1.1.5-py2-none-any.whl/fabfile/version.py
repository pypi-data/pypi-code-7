from fabric.api import local, task


@task
def bump_patch():
    """
    create a tag and commit for a new patch version
    """
    local('bumpversion patch')


@task
def bump_minor():
    """
    create a tag and commit for a new minor version
    """
    local('bumpversion minor')


@task
def bump_major():
    """
    create a tag and commit for a new major version
    """
    local('bumpversion major')
