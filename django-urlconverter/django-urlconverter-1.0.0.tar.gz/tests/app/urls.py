"""Test application urls."""


from django_urlconverter import converted_arguments_url
from django_urlconverter.urls import urls  # workaround import for Django multiple version support

urlpatterns = urls.patterns(
    'views',
    converted_arguments_url(r'^foos/<Foo:foo2>/', 'bypass'),
    converted_arguments_url(r'^noop/(?P<foo2>\w+)/$', 'bypass'),
)
