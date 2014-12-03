"""Test django urls which use converted_arguments_urlonverter.converted_arguments_url."""

from django_urlconverter import converted_arguments_url
from django_urlconverter.urls import urls  # workaround import for Django multiple version support

urlpatterns = urls.patterns(
    'views',
    converted_arguments_url(r'^noop/(?P<foo>\w+)/$', 'bypass'),
    converted_arguments_url(r'^foos/<Foo:foo>/$', 'bypass'),
    converted_arguments_url(r'^convert1/<Converter(perm=view, hello=World):converter>/$', 'bypass'),
    converted_arguments_url(r'^resources/<Foo:foo>/subresources/<Bar:bar>/$', 'bypass'),
    converted_arguments_url(r'^bars/<Bar(perm=delete, style=1, hello=world):bar>/delete/$', 'bypass'),
    converted_arguments_url(r'^app/bars/<Bar:bar1>/', urls.include('app.urls')),
    converted_arguments_url(r'^app/foos/<Foo:foo1>/', urls.include('app.urls')),
)
