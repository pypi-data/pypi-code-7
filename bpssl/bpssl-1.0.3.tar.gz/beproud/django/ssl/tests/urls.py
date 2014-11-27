#:coding=utf-8:

try:
    from django.conf.urls import patterns
except ImportError:
    # NOTE: Django <= 1.3
    from django.conf.urls.defaults import patterns

    # NOTE: For Django 1.2
    from django.conf.urls.defaults import handler404, handler500  # NOQA

from django.http import HttpResponse
from django.views.decorators.cache import never_cache

from beproud.django.ssl.decorators import ssl_view

urlpatterns = patterns(
    '',
    (r'sslurl/someurl', lambda request: HttpResponse("Spam and Eggs")),
    (r'some/other/url', lambda request: HttpResponse("Spam and Eggs")),
    (r'decorated/ssl/view', ssl_view(lambda request: HttpResponse("Spam and Eggs"))),
    # Test decorating multiple times
    (r'decorated/ssl/view', never_cache(ssl_view(lambda request: HttpResponse("Spam and Eggs")))),
)
