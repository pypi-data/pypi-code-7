# -*- coding: utf-8 -*-

"""This module provides a thin wrapper to access a PostgreSQL database,
with functions to create a connection per thread, context managers to
wrap transactions, etc"""

import psycopg2
import psycopg2.extras
import psycopg2.extensions
import threading
from contextlib import contextmanager

__VERSION__ = '0.1'
__AUTHOR__ = 'Antonio Zanardo <zanardo@gmail.com>'

_HOST = _PORT = _DB = _USER = _PASS = None

_local = threading.local()

def config_connection(host, port, database, user, password):
    global _HOST, _PORT, _DB, _USER, _PASS
    _HOST = host
    _PORT = port
    _DB = database
    _USER = user
    _PASS = password

def getdb():
    "Return a database connection object. Reuse connections on same thread"
    if not hasattr(_local, 'dbh'):
        _local.dbh = psycopg2.connect(host=_HOST, port=_PORT,
            database=_DB, user=_USER, password=_PASS,
            cursor_factory=psycopg2.extras.DictCursor)
    return _local.dbh

@contextmanager
def trans():
    "Context manager to encapsulate transaction control"
    open_trans = False
    dbh = getdb()
    if dbh.get_transaction_status() != psycopg2.extensions.TRANSACTION_STATUS_IDLE:
        open_trans = True
    c = dbh.cursor()
    try:
        yield c
    except:
        dbh.rollback()
        raise
    else:
        if not open_trans:
            dbh.commit()
    finally:
        c.close()

