# coding=utf-8
from __future__ import unicode_literals
import os
from . import Config, BASE_DIR


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

    SITE_DOMAIN = "http://localhost:3333"

    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(BASE_DIR, 'data/db/data-test.sqlite')

    # Upload config
    UPLOAD_URL = os.path.join(SITE_DOMAIN, "uploads")
