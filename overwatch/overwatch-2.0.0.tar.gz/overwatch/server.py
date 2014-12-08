import os
import socket
import bsoncoder as bson
from gevent import monkey
from struct import unpack
import select
from threading import Thread

monkey.patch_thread()
monkey.patch_time()
monkey.patch_socket()
monkey.patch_select()


class Processor(Thread):
    def __init__(self, client, callback):
        Thread.__init__(self)
        self.daemon = True
        self.client = client
        self.callback = callback
        self.project_id = None
        self.pid = None

    def drop(self):
        if self.project_id:
            self.callback('on_remove_project', (self.project_id, self.pid))

        try:
            self.client.close()
        except:
            pass

    def run(self):
        while True:
            iready, oready, eready = select.select([self.client], [], [], 1)
            if self.client in iready:
                buf = self.client.recv(4)
                if len(buf) != 4:
                    return self.drop()
                length = unpack('<I', buf)[0]
                got = 4
                data = buf
                while got < length:
                    buf = self.client.recv(512 if length - got > 512 else length - got)
                    if len(buf) == 0:
                        return self.drop()
                    data += buf
                    got += len(buf)
                try:
                    record = bson.loads(data)
                except:
                    return self.drop()
                if record.get('action') == 'hello':
                    self.project_id = record.get('project_id')
                    self.pid = record.get('pid')
                    self.callback('on_new_project', (self.project_id, self.pid))
                elif record.get('action') == 'log_event':
                    if not self.project_id:
                        return self.drop()
                    self.callback('on_log_event', (self.project_id, self.pid, record.get('record')))

class Server(Thread):
    def __init__(self, callback):
        Thread.__init__(self)
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.server.connect('/tmp/overwatch.sock')
            raise Exception('Another instance of overwatch browser is already running.')
        except socket.error:
            try:
                os.remove('/tmp/overwatch.sock')
            except OSError:
                pass
            pass

        self.server.bind('/tmp/overwatch.sock')
        self.server.listen(10)
        self.callback = callback
        self.daemon = True

    def run(self):
        while True:
            client, info = self.server.accept()
            watcher = Processor(client, self.callback)
            watcher.start()
