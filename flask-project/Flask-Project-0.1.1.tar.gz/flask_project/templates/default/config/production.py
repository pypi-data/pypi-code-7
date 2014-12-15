# coding=utf-8
from __future__ import unicode_literals
import os
from . import Config, BASE_DIR


class ProductionConfig(Config):
    # SQLAlchemy config
    # See:
    # https://pythonhosted.org/Flask-SQLAlchemy/config.html#connection-uri-format
    # http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html#database-urls
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(BASE_DIR, 'data/db/data.sqlite')

    SQLALCHEMY_BINDS = {
        #'<bd-key>': 'mysql://<user>:<password>@<host>:<port>/<db>'
    }

