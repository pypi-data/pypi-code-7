import time
import threading

from wsgiref.simple_server import make_server, WSGIRequestHandler


class QuietHandler(WSGIRequestHandler):
    def log_request(*args, **kwargs):
        pass


class LiveServer(object):
    """
    Represents a liveserver in a separate process.

    After starting, the server has three properties:
    * app
    * url
    * thread
    * port
    * server_name
    """

    def __init__(self, app):
        self.app = app

    def start(self, host='localhost', port=5555):
        """
        Start live server, setting thread and URL on self.

        Source: https://github.com/jerrykan/wsgi-liveserver/blob/master/wsgi_liveserver.py
        """

        server = make_server(
            host, port, self.app, handler_class=QuietHandler
        )

        # Create URL
        server_name = '{0}:{1}'.format(host, port)
        url = 'http://{0}'.format(server_name)

        # Set server name
        self.app.config.update({
            'SERVER_NAME': server_name
        })

        # Start the test server in the background
        thread = threading.Thread(target=server.serve_forever)
        thread.start()

        # Give the test server a bit of time to prepare for handling requests
        time.sleep(.1)

        self.server = server
        self.thread = thread
        self.url = url
        self.port = port
        self.server_name = server_name

    def stop(self):
        """ Stop live server, joining thread until terminated. """
        self.server.shutdown()

        # Join the thread until shutdown
        self.thread.join()

        assert not self.thread.is_alive()
