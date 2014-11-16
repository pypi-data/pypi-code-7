# -*- coding: utf-8 -*-
from flask.globals import g
from ...g import settings
from ...peewee_tools.base_model import gl_database_type, gl_database


def     flask_before_peewee_connect():
    if gl_database is not None and getattr(settings, 'DATABASE_CONN_STRING', None) is not None:
        g.db = gl_database
        if gl_database_type == 2:  # SQLite
            gl_database.init(settings.DATABASE_CONN_STRING, check_same_thread=False)
            g.db.connect()
            g.db.execute_sql('PRAGMA foreign_keys=ON')
        else:
            gl_database.init(settings.DATABASE_CONN_STRING)
            g.db.connect()
    else:
        g.db = None
