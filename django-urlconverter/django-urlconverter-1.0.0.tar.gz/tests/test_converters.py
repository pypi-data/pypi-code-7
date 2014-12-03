"""Tests of main functionality - converted_arguments_url function."""

import sys
import os

sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

from django.core import urlresolvers
from django.http import Http404
from django.conf import settings

urlconf = settings.ROOT_URLCONF
urlresolvers.set_urlconf(urlconf)
resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)

from django_urlconverter import converted_arguments_url
from django_urlconverter.urls import urls  # workaround import for Django multiple version support


def test_converted_arguments_url():
    """Testing resolver function with inclusion.

    URL:
    converted_arguments_url(r'^app/bars/<Bar:bar1>/', include('app.urls')),
    inlcuded
    converted_arguments_url(r'^noop/(?P<foo2>\w+)/$', 'bypass'),
    """

    res = converted_arguments_url(r'^app/bars/<Bar:bar1>/', urls.include('app.urls'))
    assert res.converters['bar1'], 'There\'s should be converter for bar1'


def test_no_conversion():
    """Testing no conversion applied even using converted_arguments_url.

    URL: converted_arguments_url(r'^noop/(?P<foo>\w+)/$', 'bypass'),
    """
    view, args, kwargs = resolver.resolve('/noop/hi/')
    data = view(None, *args, **kwargs)

    assert data['foo'] == 'hi', 'Argument shouldn\'t be converted'


def test_no_conversion_included():
    """Testing no conversion applied for another parameter.

    URL:
    converted_arguments_url(r'^app/bars/<Bar:bar1>/', include('app.urls')),
    inlcuded
    converted_arguments_url(r'^noop/(?P<foo2>\w+)/$', 'bypass'),
    """
    view, args, kwargs = resolver.resolve('/app/bars/123/noop/hi/')
    data = view(None, *args, **kwargs)

    assert data['foo2'] == 'hi', 'Argument shouldn\'t be converted'
    assert data['bar1'] == 'bar', 'Argument should be converted'


def test_conversion_1():
    """Testing conversion with 1 parameter, no inclusion.

    URL: converted_arguments_url(r'^foos/<Foo:foo>/$', 'bypass'),
    """
    view, args, kwargs = resolver.resolve('/foos/123/')
    data = view(None, *args, **kwargs)

    assert data['foo'] == 'foo', 'Argument should be converted'


def test_conversion_2():
    """Testing conversion with 2 parameters, no inclusion.

    URL: converted_arguments_url(r'^resources/<Foo:foo>/subresources/<Bar:bar>/$', 'bypass'),
    """
    view, args, kwargs = resolver.resolve('/resources/123/subresources/456/')
    data = view(None, *args, **kwargs)

    assert data['foo'] == 'foo', 'Argument should be converted'
    assert data['bar'] == 'bar', 'Argument should be converted'


def test_conversion_2_included_same_converter():
    """Testing conversion with 2 parameters with inclusion and same type of converter.

    URLs:
    converted_arguments_url(r'^app/foos/<Foo:foo1>/', include('app.urls')),
    included
    converted_arguments_url(r'^foos/<Foo:foo2>/', 'bypass'),
    """
    view, args, kwargs = resolver.resolve('/app/foos/123/foos/456/')
    data = view(None, *args, **kwargs)

    assert data['foo1'] == 'foo', 'Argument should be converted'
    assert data['foo2'] == 'foo', 'Argument should be converted'


def test_conversion_2_included_other_converter():
    """Testing conversion with 2 parameters with inclusion and other type of converter.

    URLs:
    converted_arguments_url(r'^app/bars/<Bar:bar1>/', include('app.urls')),
    included
    converted_arguments_url(r'^foos/<Foo:foo2>/', 'bypass'),
    """
    view, args, kwargs = resolver.resolve('/app/bars/123/foos/456/')
    data = view(None, *args, **kwargs)

    assert data['bar1'] == 'bar', 'Argument should be converted'
    assert data['foo2'] == 'foo', 'Argument should be converted'


def test_404():
    """Testing not found.

    URL: converted_arguments_url(r'^noop/(?P<foo>\w+)/$', 'bypass'),
    """
    try:
        resolver.resolve('/noop/!!!/')  # Pass characters that don't match the pattern
        assert False, 'Should fail with not found'
    except Http404:
        pass


def test_params_parsing():
    """Testing parameters passed to converter.

    Converter converter is assigning kwargs to self.
    URL: converted_arguments_url(r'^convert1/<Converter(perm=view, hello=World):converter>/$', 'bypass'),
    """
    view, args, kwargs = resolver.resolve('/convert1/123/')
    data = view(None, *args, **kwargs)

    converter = data['converter']
    assert converter.kwargs['perm'] == 'view', 'perm parameter should be view'
    assert converter.kwargs['hello'] == 'World', 'hello parameter should be World'
