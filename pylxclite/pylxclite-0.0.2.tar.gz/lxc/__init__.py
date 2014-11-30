import subprocess
import time
import sys
import os
import re

__all__ = ['checkconfig', 'create', 'clone', 'destroy', 'exists', 'freeze', 'info', 'ls', 'start', 'status', 'stop', 'subprocess', 'unfreeze']
        
def exists(name):
    '''
    checks if a given container is defined or not
    '''
    cmd = ['lxc-ls']
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    ret = p.communicate()[0].strip()
    if name in ret.split('\n'):
        return True
    return False

def create(name, config_file=None, template="centos", backing_store=None, template_options=None):
    '''
    Create a new container
    Default template: centos
    '''
    if exists(name):
        print "The Container %s is already created!" % name
        return 0
    cmd = 'lxc-create -n {0}'.format(name)
    cmd += ' -t {0}'.format(template)
    if config_file:
        cmd += ' -f {0}'.format(config_file)
    if backing_store:
        cmd += ' -B {0}'.format(backing_store)
            
    cmd += ' >>/dev/null'
    
    try:
        print '#####################################90%...'
        if subprocess.check_call('{0}'.format(cmd), shell=True) ==0:
            return "Container %s has been created with options %s" %(name, cmd[3:])
    except Exception, ex:
        return ex

def clone(orig=None, new=None, snapshot=False):
    '''
    Clone a container
    '''
    if orig and new:
        if exists(new):
            return 'Container {0} already exist!'.format(new)
    cmd = 'lxc-clone -o {0} -n {1}'.format(orig, new)
    if snapshot:
        cmd += ' -s'
    return subprocess.check_call('{0}'.format(cmd), shell=True)

def status(name):
    '''
    returns a list ['RUNNING'] or ['STOPPED']
    '''
    if not exists(name):
        print "The container %s does not exist!" % name
        return 0
    cmd = ["lxc-info -n %s" %name]
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    ret = p.communicate()[0].strip()
    res = r'State: +(.*)'
    stat = re.findall(res,ret)
    return stat
         
def start(name, config_file=None):
    '''
    starts a container in daemon mode
    '''
    if not exists(name):
        print "The container %s does not exist!" % name
        return 0
    if 'RUNNING' in status(name):
        print 'The container %s is already started!' % name
        return 0
    cmd = ['lxc-start', '-n', name, '-d']
    if config_file:
        cmd += ['-f', config_file]
    subprocess.check_call(cmd)
    time.sleep(2)
    return 'Oooooooooook!'

def ls():
    '''
    List containers directory
    Note: Directory mode for Ubuntu 12/13 compatibility
    '''
    cmd = ["lxc-ls"]
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    ret = p.communicate()[0].strip()
    return ret.split()

def stop(name, force=False):
    if not exists(name):
        print "The container %s does not exist!" % name
        return 0
    if 'STOPPED' in status(name):
        print 'The container %s is already stopped!' % name
        return 0
    cmd = ['lxc-stop', '-n', name]
    if force:
        cmd += ' -k'
    subprocess.check_call(cmd)
    return 'Oooooooooook!'

def destroy(name):
    '''
    removes a container [stops a container if it's running and]
    '''
    if not exists(name):
        print "The container %s does not exist!" % name
        return 0
    cmd = ['lxc-destory', '-f', '-n', name]
    subprocess.check_call(cmd)
    return 'Oooooooooook!'
        
def freeze(name):
    '''
    freezes the container
    '''
    if not exists(name):
        print "The container %s does not exist!" % name
        return 0
    if 'FROZEN' in status(name):
        return 'Oooooooooook!'
    cmd = ['lxc-freeze', '-n', name]
    subprocess.check_call(cmd)
    return 'Oooooooooook!'


def unfreeze(name):
    '''
    unfreezes the container
    '''
    if not exists(name):
        print "The container %s does not exist!" % name
        return 0
    cmd = ['lxc-unfreeze', '-n', name]
    subprocess.check_call(cmd)
    return 'Oooooooooook!'


def info(name):
    '''
    returns info dict about the specified container
    '''
    if not exists(name):
        print "The container %s does not exist!" % name
        return 0
    cmd = ['lxc-info', '-n', name]
    return subprocess.check_call(cmd)

def checkconfig():
    '''
    returns the output of lxc-checkconfig
    '''
    cmd = ['lxc-checkconfig']
    return subprocess.check_call(cmd)
