"""" 
git commands for deploy commander
"""

from fabric.api import env
from fabric.contrib.files import exists
from fabric.operations import run
from fabric.operations import prompt
from fabric.utils import abort
from fabric.colors import red
from fabric.colors import yellow
from fabric.colors import green
from fabric.contrib.console import confirm
from fabric.context_managers import cd

from fabfile import utils


def clone(params):
    install_repo(params)

def install_repo(params):
    """
    The clone command can be used to clone a new repo.
    If it's allready an existing path it will prompt for overwrite
    """
    params = utils.format_params(params)
    
    if exists(params['repo_path']):
        if confirm("Repo path `%s` found, do you want to reinstall?" % params['repo_path']):
            print(yellow("Repo path `%s` will be deleted" % params['repo_path']))
            run('rm -Rf %s' % params['repo_path'])
        else:
            abort("Aborted...")
        
    utils.ensure_path(params['repo_path'])
    run('git clone --recursive %s %s' % (params['repo_url'], params['repo_path']))
         
    print(green("Repo `%s` successfully cloned" % params['repo_url']))

def deploy_tag(params):
    """
    This command will update a repo and copy the contents to another folder.
    It can be used to create versioned deployments of the codebase
    When executed it will prompt for the tag to deploy if it's not known
    """
    params = utils.format_params(params)
    
    if 'tag' in params:
        env['params']['tag'] = params['tag']
    else:
        with cd(params['repo_path']):
            run('git fetch')
            run('git tag -l')
        
        env['params']['tag'] = prompt("Enter tag to deploy : ", default="master")
    
    tag_path = params['tag_path'] % env.params
    
    if not exists(params['repo_path']):
        abort(red("Repo path not existing... is the project installed?"))
    
    # If exist remove full source
    if exists(tag_path):
        print(yellow("Deploy source path `%s` allready existed... source data be removed and reset." % tag_path))
        run('rm -Rf %s' % tag_path)
    
    utils.ensure_path(tag_path)
    
    with cd(params['repo_path']):
        # Update local repo with latest code
        run('git checkout %s' % (env['params']['tag']))
     
        run('git pull origin %s --recurse-submodules' % (env['params']['tag']))
         
        run('git submodule update')
    
    # Copy source code to version
    run('cp -R %s/* %s' % (params['repo_path'], tag_path))
    
            