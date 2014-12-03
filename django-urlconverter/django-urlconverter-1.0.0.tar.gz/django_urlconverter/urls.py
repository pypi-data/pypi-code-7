"""Main url conversion module. Contains single public function `converted_arguments_url`
which makes urls converter-aware."""
from functools import wraps
from importlib import import_module
import re
import types

from django.conf import settings
try:
    from django.conf.urls import defaults as urls
except ImportError:
    from django.conf import urls

# Regular expression to parse converter class and it's parameters. Example: <Foo:foo2>.
RESOURCE_REGEX = re.compile(r'<(?P<converter>[A-Za-z_][A-Za-z_0-9]*)(\((?P<params>.+)\))?:(?P<variable>[^>]+)>')


def _decorate_view(func, converters, *args, **kwargs):
    """Decorates the view through the converter"""

    @wraps(func)
    def view(request, *args, **kwargs):
        for k, convert in converters.items():
            kwargs[k] = convert(kwargs.pop(k), request, *args, **kwargs)
        return func(request, *args, **kwargs)
    return view


def _resolve(self, *args, **kwargs):
    """Monkey-patch for the resolve method.

    Each time resolve is called on root converted_arguments_urlonf new instance of the match is created having original
    view function. There's no harm in wrapping it each time, because it doesn't decorate original view, but the property
    of the match.
    """

    match = self.__class__.resolve(self, *args, **kwargs)
    if match and self.converters:
        match.func = _decorate_view(match.func, self.converters, *args, **kwargs)
    return match


def _param_to_dict(params):
    """Returns the values of params as a dictionary.
    If params is empty, an empty dictionary is returned
    """
    paramsdict = {}
    if params:
        params = params.split(',')
        for param in params:
            key, value = param.split('=')
            paramsdict[key.strip()] = value.strip()
    return paramsdict


def converted_arguments_url(regex, *args, **kwargs):
    """Alternative to Django's URL (pattern) function.
    Expands resource patterns to valid RegEx named groups.
    """
    converters = {}

    def resource_match_callback(match):
        groups = match.groupdict()
        var = groups['variable']
        params = groups['params']
        conv = groups['converter']

        path = settings.URL_CONVERTERS.get(conv)
        assert path, 'Converter %s is not registered in settings.URL_CONVERTERS' % conv

        # Importing converter class
        mod, klass = path.rsplit('.', 1)
        module = import_module(mod)

        converter_class = getattr(module, klass)
        kwargs = _param_to_dict(params)
        converter = converter_class(**kwargs) if kwargs else converter_class()
        converters[var] = converter

        return '(?P<%s>%s)' % (var, getattr(converter, 'pattern', r'\d+'))

    regex = re.sub(RESOURCE_REGEX, resource_match_callback, regex)

    result = urls.url(regex, *args, **kwargs)
    if converters:
        result.converters = converters
        result.resolve = types.MethodType(_resolve, result)
    return result
