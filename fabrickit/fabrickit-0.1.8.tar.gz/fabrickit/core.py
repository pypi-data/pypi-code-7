import traceback
import os
import time
import fcntl
import tarfile
import uuid
import getpass
import collections
from fabric.api import settings, env
from fabric import api
from fabrickit.exceptions import RemoteExecutionException
from fabrickit.log import get_logger

logger = get_logger(__name__)
#Decorators
def handle_exception(func, *args, **kwargs):
    passwords = kwargs.pop('passwords', None)
    if passwords:
        if api.env.host_string in passwords:
            api.env.password = passwords[api.env.host_string]

    password = kwargs.pop('password', None)
    if password:
        api.env.password = password

    result = None
    try:
        result = func(*args, **kwargs)
    except Exception, e:
        traceback.print_exc()
        return e
    return result

def runs_once(func):
    def decorator(*args, **kwargs):
        kwargs['hosts'] = ['%s@localhost' % getpass.getuser()]
        logger.info('"%s" started with args : %s, kwargs : %s' % (func.__name__, args, kwargs))
        return execute(func, *args, **kwargs)
    return decorator

def run_multiple(func):
    def decorator(*args, **kwargs):
        logger.info('"%s" started with args : %s, kwargs : %s' % (func.__name__, args, kwargs))
        return execute(func, *args, **kwargs)
    return decorator

def emit_exception(keyfunc, ExceptionClass):
    def decorator(func):
        def wrapper(*args, **kwargs):
            rtnvals = None
            with settings(warn_only=True):
                result = func(*args, **kwargs)
                if type(result) == dict: rtnvals = { key : value for key, value in result.items() if not keyfunc(value)}
                elif type(result) == list: rtnvals = [ value for value in result if not keyfunc(value)]
                elif not keyfunc(result) : rtnvals = result
                if rtnvals:
                    e = ExceptionClass(rtnvals)
                    raise e
            return result
        return wrapper
    return decorator

@emit_exception(keyfunc=lambda result : result.return_code == 0, ExceptionClass=RemoteExecutionException)
def run(*args, **kwargs):
    return api.run(*args,**kwargs)

@emit_exception(keyfunc=lambda result : result.return_code == 0, ExceptionClass=RemoteExecutionException)
def sudo(*args, **kwargs):
    return api.sudo(*args,**kwargs)

@emit_exception(keyfunc=lambda result : result.return_code == 0, ExceptionClass=RemoteExecutionException)
def local(*args, **kwargs):
    return api.local(*args,**kwargs)

@emit_exception(keyfunc=lambda value : not isinstance(value, RemoteExecutionException), ExceptionClass=RemoteExecutionException)
def execute(func, *args, **kwargs):
    handle_exception.__name__= func.__name__
    # host='host', hosts=['host','host'], password='password, passwords={'host':'password'}
    logger.info('"%s" started with args : %s, kwargs : %s' % (func.__name__, args, kwargs))
    return api.execute(handle_exception, func, *args, **kwargs)

#Functions
def lock(source, interval=2):
    f = None
    try:
        #lock
        for f in _files(source):
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield f

    except IOError as ioe:
        time.sleep(interval)
        # Trying again
        unlock(source)
        lock(source)

    except Exception as e:
        print e
        # Terminating
        unlock(source)


def unlock(source):
    for f in _files(source):
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()


def _files(source):
    if os.path.isdir(source):
        for source, dirs, files in os.walk(source):
            for f in files:
                yield open(os.path.join(source, f), 'rb')
    else :
         yield open(source, 'rb')

def put(source, dest, use_sudo=False):
    tmp = uuid.uuid1()
    tmpsourcepath = "%s/%s.tar.gz" % (os.path.dirname(source), tmp)
    tar(source, tmpsourcepath)

    with settings(warn_only=True):
        api.put(tmpsourcepath, dest, use_sudo)

    tmpdestpath = "%s/%s.tar.gz" % (dest, tmp)
    untar(tmpdestpath, dest, local=False)

    local('rm -fr %s' % tmpsourcepath)
    run('rm -fr %s' % tmpdestpath)


def get(source, dest, use_sudo=False):

    tmp = uuid.uuid1()
    tmpsourcepath = "%s/%s.tar.gz" % (os.path.dirname(source), tmp)
    tar(source, tmpsourcepath, local_use=False)

    with settings(warn_only=True):
        api.get(tmpsourcepath, dest, use_sudo)

    tmpdestpath = "%s/%s.tar.gz" % (dest, tmp)

    local('rm -fr %s' % tmpdestpath)
    run('rm -fr %s' % tmpsourcepath)

def firewall(flag=True):
    #/usr/sbin/
    if flag:
        sudo('ufw enable')
    else:
        sudo('ufw disable')

def sudoer(user):
    sudo('if ! grep -q "%s ALL=(ALL:ALL)  NOPASSWD: ALL" /etc/sudoers ; then echo "%s ALL=(ALL:ALL)  NOPASSWD: ALL" >> /etc/sudoers; fi'  % (user,  user))

def ulimit(user, nofile=None, nproc=None, resource_limit=False):
    if nofile:
        sudo('if ! grep -q "^%s soft nofile" /etc/security/limits.conf; then echo "%s soft nofile %s" >> /etc/security/limits.conf; fi' % (user, nofile, user))
        sudo('if ! grep -q "^%s hard nofile" /etc/security/limits.conf; then echo "%s hard nofile %s" >> /etc/security/limits.conf; fi' % (user, nofile, user))

    if nproc:
        sudo('if ! grep -q "^%s soft nproc" /etc/security/limits.conf; then echo "%s soft nproc %s" >> /etc/security/limits.conf; fi' % (user, nproc, user))
        sudo('if ! grep -q "^%s hard nproc" /etc/security/limits.conf; then echo "%s hard nproc %s" >> /etc/security/limits.conf; fi' % (user, nproc, user))

    if resource_limit:
        sudo('if ! grep -q "session required pam_limits.so" /etc/pam.d/common-session; then echo "session required pam_limits.so" >> /etc/pam.d/common-session; fi')

def tar(source='./', dest='./test.tar.gz', local_use=True):
    print '[%s] tar: pressing "%s" to "%s"' % (env.host_string,source, dest)
    basedir = os.path.dirname(source)
    basename = os.path.basename(source)
    if local_use:
        cmd = 'cd %s && tar czf %s -C %s ./%s' % (basedir, dest, basedir, basename)
        if os.path.isdir(source):
            cmd =  '%s/*' % cmd
        local(cmd)

    else:
        check = run('if [ -d "./%s" ]; then echo "true"; fi')
        cmd = 'cd %s && tar czf %s -C %s ./%s' % (basedir, dest, basedir, basename)
        if check.strip() == "true":
            cmd =  '%s/*' % cmd
        run(cmd)

def untar(source='./test.tar.gz', dest='./', local=True):
    if local:
        tar = tarfile.open(source, "w:gz")
        tar.extractall(path=dest)
        tar.close()

    else:
        run('tar xzf %s -C %s' %  (source, dest))


def iter_fabric_log(pipe):
    countdict = collections.defaultdict(int)
    previous = pipe.recv()
    try:
        while True:
            if previous.startswith('['):
                name = previous[1:previous.index(']')]
                countdict[name] += 1
                msg = previous[previous.index(']')+1:]
                while True:
                    current = pipe.recv()
                    if current.startswith('['):
                        previous=current
                        break
                    else:
                        msg += current.strip()
                        previous=current
                log = { "ip" : name , "message" : msg, "num" : countdict[name]}
                yield log
            else:
                previous = pipe.recv()
    except EOFError:
        yield None

def get_hostname():
    return run('hostname')


def daemon(cmd, *args, **kwargs):
    use_sudo = kwargs.pop('use_sudo', False)
    if use_sudo:
        sudo("sh -c '((nohup %s > /dev/null 2> /dev/null) & )'" % cmd, pty=False, *args, **kwargs)
    else:
        run("sh -c '((nohup %s > /dev/null 2> /dev/null) & )'" % cmd, pty=False, *args, **kwargs)
