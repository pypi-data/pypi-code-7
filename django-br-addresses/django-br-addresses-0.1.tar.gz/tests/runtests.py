#!/usr/bin/env python
import sys
import os
from django.core.management import execute_from_command_line
import django
from django.conf import settings


if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.contrib.redirects.middleware.RedirectFallbackMiddleware'
        ),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.admin',
            'django.contrib.redirects',

        ),
        SITE_ID = 1,
        # TEST_RUNNER = 'django_coverage.coverage_runner.CoverageRunner',
        HAYSTACK_CONNECTIONS = {
            'default': {
                'ENGINE': 'haystack.backends.simple_backend.SimpleEngine'
            }
        },
        TEST_RUNNER = "django_nose.NoseTestSuiteRunner",
        TEST_DISCOVER_PATTERN = "test_*",
        NOSE_ARGS = [
            '--verbosity=2',
            '-x',
            '-d',
            '--with-specplugin',
            '--with-xtraceback',
            '--with-progressive',
        ],
    )


def runtests():
    argv = [sys.argv[0], 'test']
    execute_from_command_line(argv)
    sys.exit(0)


if __name__ == '__main__':
    runtests()
