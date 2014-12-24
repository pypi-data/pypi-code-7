from __future__ import absolute_import, division, print_function

from collections import Counter
import logging
import os.path as path
import urllib

from bs4 import BeautifulSoup
import bottle
import requests

from dossier.fc import FeatureCollection, StringCounter
from dossier.models.pairwise import dissimilar, similar
from dossier.web import \
    get_application, run_with_argv, engine_random, engine_index_scan


logger = logging.getLogger(__name__)
web_static_path = path.join(path.split(__file__)[0], 'static')
bottle.TEMPLATE_PATH.insert(0, path.join(web_static_path, 'tpl'))


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


class index_scan_make_fc(engine_index_scan):
    '''Index scan with FC materialization.

    This search engine knows the format of a particular breed of content
    id, which enables this search engine to create FCs for that id.

    Namely, if a content_id starts with ``web|``, then everything following
    that prefix is a URL. We try to do a very basic and minimal crawl of
    that URL to produce an FC to query with.
    '''
    def get_query_fc(self, content_id):
        fc = super(index_scan_make_fc, self).get_query_fc(content_id)
        if fc is not None:
            return fc
        if not content_id.startswith('web|'):
            return None
        url = urllib.unquote(content_id.split('|', 1)[1])
        soup = BeautifulSoup(requests.get(url).text)
        body = soup.find('body').get_text().strip()
        bodyBow = Counter(body.split())
        fc = FeatureCollection({
            u'title': soup.find('title').get_text(),
            u'snippet': body,
            u'snippetBow': StringCounter(dict(bodyBow.most_common(10))),
        })
        self.store.put([(content_id, fc)])
        return fc


def main():
    engines = {
        'dissimilar': dissimilar,
        'similar': similar,
        'random': engine_random,
        'index_scan': index_scan_make_fc,
    }
    args, application = get_application(routes=[add_routes],
                                        search_engines=engines)
    run_with_argv(args, application)


if __name__ == '__main__':
    main()
