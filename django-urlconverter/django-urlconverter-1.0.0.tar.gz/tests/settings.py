"""Test django settings."""

DEBUG = True

INSTALLED_APPS = (
    'app',
)

ROOT_URLCONF = 'urls'

URL_CONVERTERS = {
    'Foo': 'converters.foo.Foo',  # Converts to 'foo'
    'Bar': 'converters.bar.Bar',  # Converts to 'bar'
    'Converter': 'converters.foo.Converter',  # Converts to self for inspecting
}

SECRET_KEY = 'some secret'
