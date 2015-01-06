# encoding: utf-8
import os
import sys
import ConfigParser
import yaml
import getpass
from edopkg import config, pyaml
from config import DEFAULT_PATH, CLIENT_ID, CLIENT_SECRET
from utils import get_wo_client
from package import EdoPackage

reload(sys)
sys.setdefaultencoding('utf-8')

HELP_INFO = 'edopkg ...'
PKG_COMMAND = ['clone', 'push', 'pull', 'server']

def main():
    # 1. 命令解析
    if len(sys.argv) < 2:
        print HELP_INFO
        return

    cmd, path_filter = sys.argv[1], ''
    if cmd == 'clone':
        pkg_name = sys.argv[2]
    elif len(sys.argv) > 2:
        path_filter = sys.argv[2]

    if cmd not in PKG_COMMAND:
        print 'command error'
        return

    # 2. 读取配置
    edopkg_config_path = os.path.normpath(os.path.expanduser(DEFAULT_PATH))
    if cmd == 'server':
        section = sys.argv[2]
        # 重新设置服务器配置
        cf = ConfigParser.ConfigParser()
        cf.read(edopkg_config_path)
        cf.set('edopkg', 'server', section)
        cf.write(open(edopkg_config_path, 'w'))
        print u' 默认配置已经修改为：' + section
        return

    if not os.path.exists(edopkg_config_path):
        # 初始化配置文件
        section, oc_api, account, instance, username, password = read_inputs()
        init_config(edopkg_config_path, section, oc_api, account, instance,
                    username, password)

    cf = ConfigParser.ConfigParser()
    cf.read(edopkg_config_path)
    section = cf.get('edopkg', 'server')
    edo_config = dict(cf.items(section))

    # 3. 生成服务端连接
    wo_client = get_wo_client(  edo_config['oc_api'],
                                edo_config['client_id'],
                                edo_config['client_secret'],
                                edo_config['account'],
                                edo_config['instance'],
                                edo_config['username'],
                                edo_config['password'])

    # 初始化包管理器
    if cmd == 'clone':
        local_root = os.path.abspath(pkg_name)
        if not os.path.exists(local_root):
            os.makedirs(local_root)
        else:
            print 'package already exited'
            return
    else:
        local_root = find_package_root()
        if not local_root:
            print 'can not find the package'
            return
    edo_pkg = EdoPackage(wo_client, local_root)

    # 计算path_filter: 相对于local_root的子路径
    if path_filter:
        path_filter = os.path.relpath(os.path.abspath(path_filter), local_root)
        if path_filter == '.': # 当前文件夹
            path_filter = ''

    # 执行命令
    if cmd == 'pull':
        edo_pkg.pull(path_filter)
    elif cmd == 'push':
        edo_pkg.push(path_filter)
    elif cmd == 'clone':
        try:
            edo_pkg.pull()
        except:
            os.remove(local_root)

def init_config(path, section, oc_api, account, instance, username, password):
    cf = ConfigParser.ConfigParser()
    cf.add_section('edopkg')
    cf.set('edopkg', 'server', section)
    cf.add_section(section)
    cf.set(section, 'client_id', CLIENT_ID)
    cf.set(section, 'client_secret', CLIENT_SECRET)
    cf.set(section, 'oc_api', oc_api)
    cf.set(section, 'account', account)
    cf.set(section, 'instance', instance)
    cf.set(section, 'username', username)
    cf.set(section, 'password', password)
    cf.write(open(path, 'w'))

def read_inputs():
    print u'''
 -----------------------------
 需要输入配置信息以进行初始化
 -----------------------------'''
    section = get_input(u' 请输入配置名： ', default= 'test')
    print u'''
 -----------------------------
 请输入具体的配置数据
 -----------------------------
 字段的具体含义：

 oc_api: oc服务地址
 account: 公司(子域名)名称
 instance: 站点实例， 只有一个站点时为default
 username: 用户名
 password: 密码
 -----------------------------
 请输入数据：
 '''
    while True:
        oc_api = get_input(' oc_api[https://oc-api.everydo.cn]: ',
                           default=r'https://oc-api.everydo.cn')
        account = get_input(' account: ')
        instance = get_input(' instance[default]: ', default='default')
        username = get_input(' username: ')

        print u'''
 -----------------------------
 您的输入：
 -----------------------------'''
        print ' oc_api: %s' % oc_api
        print ' account: %s' % account
        print ' instance: %s' % instance
        print ' username: %s' % username
        print u'''
 -----------------------------
 您确认要输入的是以上的数据么？[y/n]（确认：y | 重新输入：n）：'''
        if raw_input().lower() == 'y':
            break
        else:
            print u'请重新输入数据:'

    while True:
        password = getpass.getpass('password: ')
        confirm_pwd = getpass.getpass('confirm password: ')
        if password == confirm_pwd:
            break
        else:
            print u'两次输入的密码不一致,  请重新输入'
    return section, oc_api, account, instance, username, password

def get_input(msg, default =''):
    sys.stdout.write(msg)
    input_info = raw_input()
    return input_info if input_info else default

def find_package_root():
    # 优先在当前目录下查找
    base_path = os.getcwd()
    config_path = os.path.join(base_path, 'config.yaml')
    # 不存在时往上级查找
    while not os.path.exists(config_path):
        if base_path != os.path.dirname(base_path):
            base_path = os.path.dirname(base_path)
            config_path = os.path.join(base_path, 'config.yaml')
        else:
            # 到达根时退出
            return False
    return base_path

if __name__ == '__main__':
    main()
