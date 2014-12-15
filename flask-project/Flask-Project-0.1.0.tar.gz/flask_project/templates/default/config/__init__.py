# coding=utf-8
from __future__ import unicode_literals
import os
from datetime import timedelta


# project root
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config(object):
    """Base Common Configuration"""
    def __init__(self):
        pass

    @staticmethod
    def init_app(app):
        pass

    # Flask app config
    DEBUG = False
    TESTING = False
    SECRET_KEY = '%(SECRET_KEY)s'
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7
    SESSION_COOKIE_NAME = '%(PROJECT_NAME)_session'

    # site
    SITE_NAME = "%(SITE_NAME)s"
    SITE_BRAND = "%(SITE_BRAND)s"
    SITE_DOMAIN = "http://www.%(PROJECT_NAME)s.com"
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'webee loves vivian.'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # cache
    CACHE_TYPE = 'filesystem'
    CACHE_DIR = os.path.join(BASE_DIR, 'data', 'cache')

    # scripts
    SCRIPT_DIR = os.path.join(BASE_DIR, 'scripts')

    # user
    ENABLE_LOGIN = True

    # Mail
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SYSTEM_MAIL_SUBJECT_PREFIX = '[%s]' % SITE_NAME
    SYSTEM_MAIL_SENDER = SITE_NAME + ' <system@%(PROJECT_NAME)s.com>'
    SYSTEM_ADMINS = ["hyperwood.yw@gmail.com"]

    # Redis
    REDIS = False  # 是否启用Redis
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 1

    # cache
    CACHE_TYPE = 'filesystem'
    CACHE_DIR = os.path.join(BASE_DIR, 'data', 'cache')

    # scripts
    SCRIPT_DIR = os.path.join(BASE_DIR, 'scripts')

    # Upload config
    UPLOADS_DEFAULT_DEST = os.path.join(BASE_DIR, "data/uploads")
    UPLOADS_DEFAULT_URL = os.path.join(SITE_DOMAIN, "uploads")

    # Flask-DebugToolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # Sentry config
    SENTRY_DSN = ''
    SENTRY_USER_ATTRS = ['username', 'email']

    # Host string, used by fabric
    HOST_STRING = "<usr>@host"


from .testing import TestingConfig
from .development import DevelopmentConfig
from .production import ProductionConfig

CONFIGS = {'development': DevelopmentConfig,
           'testing': TestingConfig,
           'production': ProductionConfig,
           'default': DevelopmentConfig}
