# -*- coding: utf-8 -*-
import os

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

SECRET_KEY = 'sassycoffee123'

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
STATIC_ROOT = os.path.join(PROJECT_PATH, 'data')
STATIC_URL = '/data/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

DJANGO_SASSY_COFFEE_FORMATS = [
        'sass',
        'coffee'
    ]

DJANGO_SASSY_COFFEE_EXCLUSIONS = [
    'base.sass'
]
