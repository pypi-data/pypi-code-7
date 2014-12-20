# coding: utf-8
from __future__ import unicode_literals

import sys

def unload_django_ses():
    del sys.modules['django_ses.settings']
    del sys.modules['django_ses']
