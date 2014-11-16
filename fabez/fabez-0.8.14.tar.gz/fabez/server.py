# -*- coding: utf-8 -*-

import tempfile

from fabric.api import *

from fabez.cmd import *
from server import *
from io import *
from perm import *
from utils import *
from pythonic import *
from etc import *


try:
    import pkg_resources  # in package
except:
    pass


def server_nginx(user=None, worker_processes=1, worker_connections=512, old_user='nginx', error_log='/logs/nginx/error.log', access_log='/logs/nginx/access.log'):
    """
    Install Nginx
    :param user: user,default is nobody
    :param worker_processes: process numbers
    :param worker_connections: connections numbers
    :return:None
    """

    run('yum install nginx -y')

    run('chkconfig --level 35 nginx on')

    # custom config
    if user:
        run('sed -i -e "s/\(user\s*\)%s/\\1%s/g" /etc/nginx/nginx.conf' % (old_user, user))
    run('sed -i -e "s/\(worker_processes\s*\)[0-9]*/\\1%d/g" /etc/nginx/nginx.conf' % worker_processes)
    run('sed -i -e "s/\(worker_connections\s*\)[a-zA-Z\/._0-9]*/\\1%d/g" /etc/nginx/nginx.conf' % worker_connections)
    run('sed -i -e "s/\(error_log\s*\)[a-zA-Z\/._0-9]*/\\1%s/g" /etc/nginx/nginx.conf' % error_log.replace('/', '\/'))
    run('sed -i -e "s/\(access_log\s*\)[a-zA-Z/._0-9]*/\\1%s/g" /etc/nginx/nginx.conf' % access_log.replace('/', '\/'))


def rm_server_nginx():
    """
    unintall nginx
    :return:
    """

    with settings(warn_only=True):
        run('chkconfig --level 35 nginx off')
        run('yum erase nginx -y')
        run('rm -rf /etc/nginx')

    pass


def server_redis(card='eth0', size=None, newer='remi'):
    """
    Install redis server
    @todo support set unixsocket
    @todo support change maxsize
    @todo support change database numbers
    :return:
    """

    with settings(warn_only=True):
        run('mkdir -p /storage/redis')

    yum_install('redis', newer='remi')

    run('chown redis.redis /storage/redis')
    run('chkconfig --level 35 redis on')

    ip = cmd_ip(card)
    run('sed -i -e "s/\(bind\s*\)[0-9\.]*/\\1%s/g" /etc/redis.conf' % ip)

    # if size:
    # run('sed -i -e "s/\(^maxmemory \s*\)[0-9\.]*/\\1%s/g" /etc/redis.conf' % ip)


    pass


def rm_server_redis(clean=False):
    """
    Remove redis server
    :param clean:
    :return:
    """
    run('yum earse redis -y')

    if clean is True:
        run('rm -rf /storage/redis')

    pass


def server_mongo(card='lo'):
    """
    @note this mongo only support 64-bit system
    :return:
    """

    try:
        buf = pkg_resources.resource_string('fabez', 'tpl/mongodb.repo')
    except:
        buf = open(os.path.join(os.path.dirname(__file__), 'tpl', 'mongodb.repo')).read()
        pass

    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/yum.repos.d/mongodb.repo')
    os.remove(fh.name)

    run('yum install mongodb-org -y')

    if card:
        ip = cmd_ip(card)
        run('sed -i -e "s/\(bind_ip\s*=\s*\)[0-9\.]*/\\1%s/g" /etc/mongod.conf' % ip)

    run('chkconfig --level 35 mongod on')
    pass


def server_gitolite(pubkey=None):
    '''
    @TODO. create gitolite server
    :param pubkey:
    :return:
    '''
    run('yum install gitolite3 -y')
    if pubkey is None:
        run('cp ~/.ssh/authorized_keys /tmp/gitolite.pub')
    else:
        put_public_key(pubkey, '/tmp/gitolite.pub')

    run('chown gitolite3 /tmp/gitolite.pub')
    cmd_su('gitolite setup -pk /tmp/gitolite.pub', 'gitolite3')

    pass


def server_supervisor(user='webuser', tmp='/tmp', log_dir='/logs/supervisor', log_level='info'):
    """
    Install supervisor
    """

    # yum supervisor id tooooooooooooooooo old
    # run('yum install supervisor -y')

    # try:
    # buf = pkg_resources.resource_string('fabez', 'tpl/supervisord.boot')
    # except:
    # buf = open(os.path.join(os.path.dirname(__file__), 'tpl', 'supervisord.boot')).read()
    #     pass
    #
    # with tempfile.NamedTemporaryFile('w', delete=False) as fh:
    #     print>> fh, buf
    #
    # put(fh.name, '/etc/init.d/supervisord')
    # os.remove(fh.name)

    # run('chkconfig --level 35 supervisord on')


    with settings(warn_only=True):
        if run('cat /etc/rc.local | grep "/usr/local/bin/supervisord"').failed:
            run('echo "/usr/local/bin/supervisord -c  /etc/supervisord.conf " >> /etc/rc.local')

    with settings(warn_only=True):
        run('test -d /etc/supervisor.d || mkdir /etc/supervisor.d')

    try:
        template = pkg_resources.resource_string('fabez', 'tpl/supervisord.conf')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'supervisord.conf')).read()
        pass

    buf = template.replace('{$username}', user) \
        .replace('{$tmp}', tmp) \
        .replace('{$logs}', log_dir) \
        .replace('{$log_level}', log_level)


    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/supervisord.conf')
    os.remove(fh.name)

    pass


def server_websuite(user='webuser', python_version='3.4.2', only_pypy=True, pypy_version='2.4', compatible=False):
    run('yum install wget -y')

    cmd_useradd(user)
    cmd_ulimit()
    utils_epel()

    utils_git()

    io_webdata(uid=user, gid=user)

    io_slowlog('nginx', user)
    # server_nginx(user)
    server_tengine(user)

    io_slowlog('supervisor', user)
    server_supervisor()

    if only_pypy:
        py_pypy(pypy_version)

    else:
        py_python(python_version, compatible=compatible, pypy=pypy_version)


    pip('tornadoez')
    pip('pyjwt')

    utils_imagelib()
    pip_c('pillow')
    pip('pymongo')
    pip('redis')
    pip('pymysql')

    pass


def server_mysql():
    with settings(warn_only=True):
        run('rpm -Uvh http://dev.mysql.com/get/mysql-community-release-el6-5.noarch.rpm')

    run('yum install mysql-community-server -y')
    run('chkconfig --level 35 mysqld on')
    pass





def server_tengine(version='2.0.3', user='webuser', tornado=True,process=1,connection=1024):
    """
    syslog note
    # need change config use syslog-ng
    # source s_sys {
    #         file ("/proc/kmsg" program_override("kernel: "));
    #         unix-dgram ("/dev/log");
    #         internal();
    #         udp(ip(0.0.0.0) port(514));
    #     };

    # gd-progs use for image-fliter

    :param version:
    :param user:
    :param tornado:
    :return:
    """

    with settings(warn_only=True):
        run('service tengine stop')


    utils_baselib()
    run('yum install jemalloc jemalloc-devel  -y')
    run('yum install GeoIP GeoIP-devel GeoIP-update GeoIP-update6 -y')
    run('yum install pcre-devel openssl-devel nginx -y')

    run('chkconfig --level 35 nginx off')

    run('wget http://tengine.taobao.org/download/tengine-{0}.tar.gz -O /tmp/tengine-{0}.tar.gz'.format(version))

    io_slowlog('nginx', user=user)
    io_aircache('nginx', size=1)

    run('test -d /usr/local/var/lock || mkdir -p /usr/local/var/lock')


    with cd('/tmp'):
        run('tar -xvzpf tengine-{0}.tar.gz'.format(version))
        with cd('/tmp/tengine-{0}'.format(version)):

            if tornado:
                run('./configure --prefix=/usr/local --user={0} --group={0} --conf-path=/etc/nginx  --sbin-path=/usr/local/sbin '
                    ' --without-http_fastcgi_module --without-http_uwsgi_module --without-http_scgi_module --without-http_memcached_module --without-http_autoindex_module '
                    ' --without-http_auth_basic_module'
                    ' --with-http_spdy_module'
                    ' --with-jemalloc --with-http_spdy_module'
                    ' --with-http_realip_module'
                    ' --with-http_concat_module '

                    #dir path
                    '--pid-path=/usr/local/var/run/nginx.pid --lock-path=/usr/local/var/lock/nginx '

                    #file path
                    ' --http-client-body-temp-path=/aircache/nginx/body_temp'
                    ' --http-proxy-temp-path=/aircache/nginx/proxy_temp'
                    ' --error-log-path=/logs/nginx/error.log --http-log-path=/logs/nginx/access.log'
                    ' --with-syslog'
                    # ' --with-http_reqstat_module'
                    ' --with-http_stub_status_module'
                    ' --with-http_geoip_module'

                    ' --with-http_gzip_static_module'
                    ' --with-http_ssl_module'
                    ' --with-pcre'
                    ' --with-file-aio'

                    # ' --with-http_upstream_keepalive_module'

                    ' --with-http_ssl_module '
                    ' --with-http_footer_filter_module=shared'
                    ' --with-http_sysguard_module=shared'
                    ' --with-http_addition_module=shared'
                    # ' --with-http_xslt_module=shared'
                    # ' --with-http_image_filter_module=shared'
                    ' --with-http_rewrite_module=shared '
                    ' --with-http_sub_module=shared'
                    ' --with-http_flv_module=shared'
                    ' --with-http_slice_module=shared'
                    ' --with-http_mp4_module=shared'
                    ' --with-http_random_index_module=shared'
                    ' --with-http_secure_link_module=shared'
                    ' --with-http_sysguard_module=shared'
                    ' --with-http_charset_filter_module=shared'
                    ' --with-http_userid_filter_module=shared'


                    ' --with-http_footer_filter_module=shared'.format(user))

            run('make && make install')
            pass


    try:
        template = pkg_resources.resource_string('fabez', 'tpl/nginx.conf')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'nginx.conf')).read()
        pass

    buf = template.replace('{$user}', user) \
        .replace('{$process}', str(process)) \
        .replace('{$connection}', str(connection))

    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/nginx/nginx.conf')

    os.remove(fh.name)


    try:
        template = pkg_resources.resource_string('fabez', 'tpl/nginx.start')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'nginx.start')).read()
        pass

    buf = template

    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/init.d/tengine')

    os.remove(fh.name)


    try:
        template = pkg_resources.resource_string('fabez', 'tpl/nginx.sysconfig')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'nginx.sysconfig')).read()
        pass

    buf = template

    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/sysconfig/nginx')

    os.remove(fh.name)


    run('chmod +x  /etc/init.d/tengine')
    run('chkconfig --level 35 tengine on')
    pass







def supervisor_restart():
    run('killall supervisord')
    run('`grep supervisor /etc/rc.local`')

