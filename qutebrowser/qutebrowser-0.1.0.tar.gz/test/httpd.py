import os
import os.path

import cherrypy
from cherrypy import _cplogging


urls = []


class LogManager(_cplogging.LogManager):

    def access(self):
        method, url, version = cherrypy.request.request_line.split(' ')
        if method != 'GET':
            raise ValueError("Got non-GET request!")
        urls.append(url)
        print("accessed: {}".format(url))
        super().access()


class Server:

    pass


def start_server():
    conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '',
        }
    }
    app = cherrypy.tree.mount(Server(), '/', conf)
    app.log = LogManager()
    cherrypy.engine.start()


if __name__ == '__main__':
    start_server()
    cherrypy.engine.block()
