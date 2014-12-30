# -*- coding: utf-8 -*-

from optparse import make_option

from django.conf import settings

from django.core.files.storage import get_storage_class
from django.core.management.base import CommandError
from django.contrib.staticfiles.management.commands import collectstatic
from django.contrib.staticfiles.storage import staticfiles_storage


class Command(collectstatic.Command):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.storage = get_storage_class('django.contrib.staticfiles.storage.StaticFilesStorage')()
        self.local = True

