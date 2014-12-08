#!/usr/bin/env python2

from flask import Flask, send_file
from flask.ext.socketio import SocketIO
from server import Server
from gevent import monkey
from Queue import Queue, Empty
from threading import Thread
import time
import pkg_resources
import json
import sys
import os
import re

monkey.patch_thread()
monkey.patch_time()
monkey.patch_socket()

class Config:
    HOST_NAME = '127.0.0.1'
    PORT_NUMBER = 31337
    SECRET_KEY = 'supersecret!'

get_resource_path = lambda filename: pkg_resources.resource_filename('overwatch', os.path.join('data', filename))


app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

# Server handlers

class Processor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

        self.projects = []
        self.events = Queue()

    def run(self):
        while True:
            time.sleep(0)
            event, args = self.events.get()
            getattr(self, event)(*args)

    def on(self, event, args):
        self.events.put((event, args))

    def on_new_project(self, name, pid):
        self.projects.append((name, pid))
        socketio.emit('projects:new', json.dumps(dict(id=pid, name=name, color=crc(pid))), True)
#        send_project_list()
        print 'New project: {} [{}]'.format(name, pid)

    def on_remove_project(self, name, pid):
        try:
            self.projects.remove((name, pid))
        except ValueError:
            pass
        socketio.emit('projects:remove', json.dumps(dict(id=pid)), True)
#        send_project_list()
        print 'Disconnected: {} [{}]'.format(name, pid)

    def on_log_event(self, name, pid, data):
        data['msg'] = data['msg'].strip()
        print ' * Sending...'
        socketio.emit('log-items:new', json.dumps(dict(project=dict(id=pid, name=name, color=crc(pid)), data=data)), True)
        print ' * Sent'
#        print 'Log: {}: {}'.format(name, data)

processor = Processor()
processor.start()


def fn():
    import time
    while True:
        socketio.emit('ping', 'data', True)
        time.sleep(0)
        time.sleep(0.25)

import threading
threading.Thread(target=fn).start()


# Shared methods

CRC_COLORS = [
    '#AA7777',
    '#77AA77',
    '#7777AA',
    '#AA0077',
    '#AA7700',
    '#00AA77',
    '#77AA00',
    '#0077AA',
    '#7700AA',
    '#AA0000',
    '#00AA00',
    '#0000AA',
    '#00AAAA',
    '#AA00AA',
    '#AAAA00',
    '#77AAAA',
    '#AA77AA'
]

def crc(s):
    return CRC_COLORS[sum([ord(x) for x in str(s)]) % len(CRC_COLORS)]


# Flask handlers

@app.route('/pkg/<path:path>')
def pkg_static(path):
    return send_file(get_resource_path(path))

@app.route('/')
def index():
    return send_file(get_resource_path('index.html'))

# SocketIO handlers

@socketio.on('projects:get-list()')
def project_list():
    socketio.emit('projects:list', json.dumps([dict(name=x[0], id=x[1], color=crc(x[1])) for x in processor.projects]))

server = Server(processor.on)
server.start()

socketio.run(app, host=Config.HOST_NAME, port=Config.PORT_NUMBER)

gui = GUI()
gui.main()
