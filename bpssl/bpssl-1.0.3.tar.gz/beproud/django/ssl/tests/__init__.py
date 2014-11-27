# NOTE: Tests are imported in this file to support Django < 1.6.
#       The test runner in Django 1.6 and above does not recognize
#       tests in this file because it (__init__.py) does not match
#       the pattern test*.py.

from beproud.django.ssl.tests.test_wsgi import *  # NOQA
from beproud.django.ssl.tests.test_proxy import *  # NOQA
from beproud.django.ssl.tests.test_context_processors import *  # NOQA
