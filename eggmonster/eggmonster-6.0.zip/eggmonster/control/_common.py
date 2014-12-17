import os
import posixpath
import re
import ConfigParser
import signal
import json

import requests

from eggmonster import emenv, __version__

session = requests.session()
session.headers['User-Agent'] = 'Eggmonster/%s' % __version__

def get_auth():
    pypirc = os.path.expanduser('~/.pypirc')
    if not os.path.isfile(pypirc):
        return

    parser = ConfigParser.ConfigParser()
    parser.readfp(open(pypirc))
    try:
        username = parser.get('server-login', 'username')
        password = parser.get('server-login', 'password')
        return username, password
    except:
        pass

def get_json(url):
    server = emenv.master

    server_url = posixpath.join(server, url)
    resp = session.get(server_url, auth=get_auth())
    resp.raise_for_status()
    if resp.status_code != 200:
        msg = ("Non-200 response code back from server: "
            "{resp.status} - {server_url}").format(**vars())
        raise AssertionError(msg)

    return resp.json()

def request(url, data, method='PUT', check_status=True):
    server = emenv.master
    server_url = posixpath.join(server, url)
    resp = session.request(url=server_url, method=method, data=data,
        auth=get_auth())
    if check_status:
        resp.raise_for_status()

    return resp

MINFACT = 60
HOURFACT = MINFACT * 60
DAYFACT = HOURFACT * 24
def timestr(s, max=0, depth=0):
    if max and depth == max:
        return ''
    if s >= DAYFACT:
        return ('%dd ' % (s / DAYFACT)) + timestr(s % DAYFACT, max, depth+1)
    if s >= HOURFACT:
        return ('%dh ' % (s / HOURFACT)) + timestr(s % HOURFACT, max, depth+1)
    if s >= MINFACT:
        return ('%dm ' % (s / MINFACT)) + timestr(s % MINFACT, max, depth+1)
    return '%ds' % s

def stat_to_node_def(line):
    package, app, host, num = stat_line.match(line).groups()
    return package, app, host, int(num)

stat_line = re.compile(r"^(.+?)\.(.+?) \((.+):([0-9]+)\) .*$")

def stat_to_args(fd):
    nodes = [stat_to_node_def(line) for line in fd]
    return dict(node_json=json.dumps(nodes))

def control_command(fd, cmd):
    nodes = stat_to_args(fd)
    request(url=cmd, data=nodes, method='POST')

def reset_sigpipe():
    """
    cope with broken pipes
    """
    if hasattr(signal, 'SIGPIPE'):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def reset_sigint():
    "handle keyboard interrupts nicely"
    signal.signal(signal.SIGINT, signal.SIG_DFL)
