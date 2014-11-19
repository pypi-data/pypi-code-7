from tornado.ioloop import PeriodicCallback
from codex.tornado.datetime import date
from tornado.web import HTTPError

import pymongo
import hashlib
import uuid

_DATABASE_NAME = '_tornado_sessions'

class SessionStorage:

    gc = None
    engine = None
    gc_activated = False

    @staticmethod
    def set_engine(settings):

        if 'storage_host' in settings and not settings['storage_host']:
            settings['storage_host'] = 'localhost'
        if 'storage_port' in settings and not settings['storage_port']:
            settings['storage_port'] = 27017
        if 'storage_name' not in settings or not settings['storage_name']:
            raise HTTPError(500, 'Session Storage name must be defined')

        client = pymongo.MongoClient(settings['storage_host'], int(settings['storage_port']), max_pool_size=200)
        SessionStorage.engine = client[_DATABASE_NAME][settings['storage_name']]

    @staticmethod
    def do_gc():
        pass

    @staticmethod
    def set_gc(main_ioloop, interval):
        SessionStorage.gc = PeriodicCallback(SessionStorage.do_gc, interval, io_loop=main_ioloop)
        SessionStorage.gc.start()
        SessionStorage.gc_activated = True

class Session:

    def __init__(self, controller, config):

        self._is_new = False
        self._is_modified = False
        self._is_destroyed = False
        self._controller = controller
        self._config = config

        session_id = self._controller.get_secure_cookie(self._config['cookie_name'])
        if not session_id:
            session_id = str(uuid.uuid4()).replace('-', '')
            self._controller.set_secure_cookie(self._config['cookie_name'], session_id, None)
        else:
            session_id = session_id.decode()

        self._generate_id(session_id)

        self._data = {}
        self._conn = SessionStorage.engine

        data = { '_id' : self.id }
        data = self._conn.find_one(data)
        if data is None:

            self._is_new = True
            self._data['_id'] = self.id
            self._data['sess_data'] = {}
            self._data['ip_address'] = self.ip_address
            self._data['user_agent'] = self.user_agent
            self._data['created_at'] = date()

        elif data['ip_address'] != self.ip_address or data['user_agent'] != self.user_agent:

            self._is_modified = True
            self._data['_id'] = self.id
            self._data['sess_data'] = {}
            self._data['ip_address'] = self.ip_address
            self._data['user_agent'] = self.user_agent
            self._data['created_at'] = date()

        else:
            self._data = data

    def _generate_id(self, session_id):
        self.ip_address = self._controller.request.remote_ip
        self.id = hashlib.sha1(('{' + session_id + self.ip_address + '}').encode()).hexdigest()
        self.user_agent = self._controller.request.headers['User-Agent'][:120]

    def regenerate_id(self, delete_old_session=False):

        old_id = self.id
        session_id = str(uuid.uuid4()).replace('-', '')
        self._controller.set_secure_cookie(self._config['cookie_name'], session_id, None)
        self._generate_id(session_id)

        self._data['_id'] = self.id
        self._data['ip_address'] = self.ip_address
        self._data['user_agent'] = self.user_agent
        if delete_old_session:
            self._data['sess_data'] = {}
            self._data['created_at'] = date()
        self._conn.remove({ '_id' : old_id })
        self._conn.insert(self._data)
        
    def get(self, name, default=None):
        return self._data['sess_data'].get(name, default)

    def flash(self, name, default=None):
        if name in self._data['sess_data']:
            result = self._data['sess_data'][name]
            self.remove(name)
            return result
        return default

    def set(self, name, value):
        self._data['sess_data'][name] = value
        self._is_modified = True
        return self

    def remove(self, name):
        if name in self._data['sess_data']:
            del self._data['sess_data'][name]
            self._is_modified = True
        return self

    def all(self):
        return self._data['sess_data']

    def clear(self):
        self._data['sess_data'] = {}
        self._is_modified = True
        return self

    def save(self):
        if not self._is_destroyed:
            if self._is_new:
                self._conn.insert(self._data)
            elif self._is_modified:
                self._conn.update({ '_id' : self.id }, self._data)

    def destroy(self):
        self._is_destroyed = True
        self._conn.remove({ '_id' : self.id })
        self._controller.clear_cookie(self._config['cookie_name'])