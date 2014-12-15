# coding=utf-8
from __future__ import unicode_literals
import os
from . import Config, BASE_DIR


class DevelopmentConfig(Config):
    DEBUG = True
    SITE_DOMAIN = "http://localhost:2222"

    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(BASE_DIR, 'data/db/data-dev.sqlite')


    # Upload config
    UPLOAD_URL = os.path.join(SITE_DOMAIN, "uploads")
