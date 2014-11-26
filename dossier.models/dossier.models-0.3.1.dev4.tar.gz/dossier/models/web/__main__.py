from __future__ import absolute_import, division, print_function

import logging
import os.path as path

import bottle

from dossier.models.pairwise import dissimilar, similar
from dossier.web import \
    get_application, run_with_argv, engine_random, engine_index_scan


logger = logging.getLogger(__name__)
web_static_path = path.join(path.split(__file__)[0], 'static')
bottle.TEMPLATE_PATH.insert(0, path.join(web_static_path, 'tpl'))

engines = {
    'dissimilar': dissimilar,
    'similar': similar,
    'random': engine_random,
    'index_scan': engine_index_scan,
}


def add_routes(app):
    @app.get('/SortingQueue')
    def example_sortingqueue():
        return bottle.template('example-sortingqueue.html')

    @app.get('/SortingDesk')
    def example_sortingdesk():
        return bottle.template('example-sortingdesk.html')

    @app.get('/static/<name:path>')
    def v1_static(name):
        return bottle.static_file(name, root=web_static_path)


def main():
    args, application = get_application(routes=[add_routes],
                                        search_engines=engines)
    run_with_argv(args, application)

if __name__ == '__main__':
    main()
