# coding: utf-8
from __future__ import unicode_literals

import os.path
import django

SECRET_KEY = 42

INSTALLED_APPS = ['django_ses']
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = 'tests.urls'
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware')

TEST_DISCOVER_TOP_LEVEL = os.path.dirname(__file__)

if django.VERSION[:2] < (1, 6):
    # I don't get it...
    # Python 3.x complains, when test runner is specified as a byte string
    # Python 2.x/Django 1.4 complains, when it's an unicode
    TEST_RUNNER = str('discover_runner.DiscoverRunner')
