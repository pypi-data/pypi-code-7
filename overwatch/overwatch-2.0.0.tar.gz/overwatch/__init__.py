from threading import Thread
from Queue import Queue
import logging
import socket
import bsoncoder as bson
import os
import sys
import datetime
import traceback
from time import time, sleep

try:
    from twisted.python import log
    TWISTED = True
except:
    TWISTED = False


class adict(dict):
    def __init__(self, *args, **kwargs):
        super(adict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, key):
        return None


def init(id, api_key=None):
    _instance = Overwatch(id, api_key)
    _instance.start()


class Overwatch(Thread):
    class Handler(logging.StreamHandler):
        def __init__(self, callback):
            self.callback = callback
            logging.StreamHandler.__init__(self)

        def emit(self, record):
            self.callback(record)

    def __init__(self, id, api_key):
        Thread.__init__(self)
        self.daemon = True
        self.id = id
        self.api_key = api_key
        self.socket_path = '/tmp/overwatch-%s.sock' % self.id

        self._init_socket()

        self.queue = Queue()
        self.root_logger = logging.getLogger()
        self.root_logger.addHandler(Overwatch.Handler(self._process))
        self.root_logger.setLevel(logging.DEBUG)
        if TWISTED:
            observer = log.PythonLoggingObserver(loggerName='root')
            observer.start()
#            log.startLogging()
#            log.addObserver(self._process)

    def _init_socket(self):
        res = False
        while not res:
            res = self.connect()
            sleep(1)

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect('/tmp/overwatch.sock')
            self.socket.send(bson.dumps({
                'action': 'hello',
                'project_id': self.id,
                'pid': os.getpid(),
            }))
            return True
        except Exception, e:
            self.say('Could not connect: %s' % self.nice_exc(sys.exc_info()))
            return False

    def _process(self, record):
        self.queue.put(record)

    def say(self, s):
        f = open('/tmp/overwatch-client.log', 'a+')
        f.write('[OVERWATCH] %s\n' % str(s))
        f.close()

    def nice_exc(self, exc_info):
        return ''.join(traceback.format_exception(
            exc_info[0],
            exc_info[1],
            exc_info[2],
            100
        ))

    def run(self):
        while True:
            try:
                try:
                    record = self.queue.get(True, 1)
                except:
                    continue
                if record.exc_info:
                    record.msg = record.msg + '\n' + self.nice_exc(record.exc_info)
                while True:
                    try:
                        try:
                            rec_msg = record.msg % record.args
                        except TypeError:
                            rec_msg = '*FORMATTING FAILED* %s | %s' % (str(record.msg), str(record.args))
                        self.socket.send(bson.dumps({
                            'action': 'log_event',
                            'record': {
                                'source': 'python',
                                'levelname': record.levelname,
                                'levelno': record.levelno,
                                'api_key': self.api_key,
                                'module': record.module,
                                'filename': record.filename,
                                'func_name': record.funcName,
                                'lineno': str(record.lineno),
                                'msg': rec_msg,
                                'time': '%f' % time(),
                            },
                        }))
                        break
                    except Exception, e:
                        self.say('Error sending: %s, gonna reconnect in 1s.' % self.nice_exc(sys.exc_info()))
                        res = False
                        while not res:
                            sleep(1)
                            res = self.connect()
            except Exception, e:
                self.say('ERROR: %s' % e)
