# -*- coding: utf-8 -*-
from flask.globals import g


def     flask_after_peewee_close(response):
    if hasattr(g, 'db') and g.db is not None:
        try:
            g.db.close()
        except:
            pass
    return response
