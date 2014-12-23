#!/usr/bin/env python

import os

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import peewee
from rivr.middleware import Middleware

SCHEMES = {
    'postgres': 'peewee.PostgresqlDatabase',
    'postgresql': 'peewee.PostgresqlDatabase',
    'mysql': 'peewee.MySQLDatabase',
    'sqlite': 'peewee.SqliteDatabase'
}

for scheme in SCHEMES.values():
    urlparse.uses_netloc.append(scheme)


def parse_url(url):
    config = {}
    url = urlparse.urlparse(url)
    path = url.path[1:]
    path = path.split('?', 2)[0]

    config.update({
        'name': path,
        'user': url.username,
        'password': url.password,
        'host': url.hostname,
        'port': url.port,
    })

    if url.scheme in SCHEMES:
        config['engine'] = SCHEMES[url.scheme]

    return config


def get_config(env, default=None):
    url = os.environ.get(env, default)
    if url:
        return parse_url(url)


def load_database(config):
    name = config.pop('name')
    _, engine = config.pop('engine').split('.', 2)
    config = dict((k, v) for k, v in config.items() if v)
    return getattr(peewee, engine)(name, **config)


class Database(Middleware):
    def __init__(self, database=None, env='DATABASE_URL', default=None):
        if database is None:
            config = get_config(env, default)
            if config:
                database = load_database(config)

        if database is None:
            raise Exception('Database is not configured.')

        self.database = database
        self.Model = self.get_model_class()

    def process_request(self, request):
        self.database.connect()

    def process_response(self, request, response):
        if not self.database.is_closed():
            self.database.close()

        return response

    def get_model_class(self):
        class Model(peewee.Model):
            class Meta:
                database = self.database

        return Model

    def wrap(self, view):
        def func(request):
            return self.dispatch(view, request)

        return func

    def __call__(self, view):
        return self.wrap(view)

    # Proxy to database

    def create_tables(self, *args, **kwargs):
        return self.create_tables(*args, **kwargs)

    def transaction(self, *args, **kwargs):
        return self.database(*args, **kwargs)

    def atomic(self, *args, **kwargs):
        return self.atomic(*args, **kwargs)
