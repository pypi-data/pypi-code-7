
from tornado.websocket import WebSocketHandler
from tornado.web import FallbackHandler
from tornado.wsgi import WSGIContainer
from json import loads
from json import dumps as jsonify


class WebSocket(WebSocketHandler):
    _socks = set()
    _onopen = None
    _onmessage = None
    _onclose = None

    @classmethod
    def onopen(cls, f):
        cls._onopen = f

    @classmethod
    def onmessage(cls, f):
        cls._onmessage = f

    @classmethod
    def onjsonmessage(cls, f):
        cls._onmessage = lambda s, m: f(s, loads(m))

    @classmethod
    def onclose(cls, f):
        cls._onclose = f

    @property
    def ip(self):
        return self.request.remote_ip

    def write_json(self, data):
        return self.write_message(jsonify(data))

    @classmethod
    def broadcast_message(cls, data, predicate=lambda socket: True):
        for sock in filter(predicate, cls._socks):
            sock.write_message(data)

    @classmethod
    def broadcast_json(cls, data, predicate=lambda socket: True):
        cls.broadcast_message(jsonify(data), predicate)

    def open(self):
        self._socks.add(self)
        if self._onopen:
            self._onopen()

    def on_message(self, msg):
        if self._onmessage:
            self._onmessage(msg)

    def on_close(self):
        self._socks.remove(self)
        if self._onclose:
            self._onclose()


def websocket(app, path, extra_attrs=None):
    sc = type(path.replace('/', '_'), (WebSocket,), extra_attrs or {})
    app.add_handlers('.*', [(path, sc)])
    return sc


def bootstrap_flask(tornado_app, flask_app):
    wsgi = WSGIContainer(flask_app)
    tornado_app.add_handlers('.*', [('.*', FallbackHandler, dict(fallback=wsgi))])
