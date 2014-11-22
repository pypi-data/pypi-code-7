"""
12factor inspired environment configuration
"""
from __future__ import unicode_literals
import os
import sys
import re
import json
import warnings
import glob
import collections
import logging

logger = logging.getLogger(__file__)

try:
    import urllib.parse as urlparse
except ImportError:
    # Python <= 2.6
    import urlparse


if sys.version < '3':
    text_type = unicode
else:
    text_type = str
    basestring = str

from .interpolation import (
    resolve, resolve_files, StringTemplate, is_variable, interpolated
)

__author__ = 'joke2k'


# return int if possible
_cast_int = lambda v: int(v) if isinstance(v, basestring) and v.isdigit() else v
# return str if possibile
_cast_str = lambda v: str(v) if isinstance(v, basestring) else v


class NoValue(object):
    def __repr__(self):
        return '<{0}>'.format(self.__class__.__name__)


class Environment(collections.MutableMapping):
    """Provide schema-based lookups of environment variables so that each
    caller doesn't have to pass in `cast` and `default` parameters.

    Usage:::

        env = Environment(MAIL_ENABLED=bool, SMTP_LOGIN=(str, 'DEFAULT'))
        if env('MAIL_ENABLED'):
            ...
    """

    NOTSET = NoValue()
    BOOLEAN_TRUE_STRINGS = ('true', 'on', 'ok', 'y', 'yes', '1')
    URL_CLASS = urlparse.ParseResult
    DEFAULT_DATABASE_ENV = 'DATABASE_URL'
    DB_SCHEMES = {
        'postgres': 'django.db.backends.postgresql_psycopg2',
        'postgresql': 'django.db.backends.postgresql_psycopg2',
        'psql': 'django.db.backends.postgresql_psycopg2',
        'pgsql': 'django.db.backends.postgresql_psycopg2',
        'postgis': 'django.contrib.gis.db.backends.postgis',
        'mysql': 'django.db.backends.mysql',
        'mysql2': 'django.db.backends.mysql',
        'mysqlgis': 'django.contrib.gis.db.backends.mysql',
        'spatialite': 'django.contrib.gis.db.backends.spatialite',
        'sqlite': 'django.db.backends.sqlite3',
        'ldap': 'ldapdb.backends.ldap',
    }
    _DB_BASE_OPTIONS = ['CONN_MAX_AGE', 'ATOMIC_REQUESTS', 'AUTOCOMMIT']

    DEFAULT_CACHE_ENV = 'CACHE_URL'
    CACHE_SCHEMES = {
        'dbcache': 'django.core.cache.backends.db.DatabaseCache',
        'dummycache': 'django.core.cache.backends.dummy.DummyCache',
        'filecache': 'django.core.cache.backends.filebased.FileBasedCache',
        'locmemcache': 'django.core.cache.backends.locmem.LocMemCache',
        'memcache': 'django.core.cache.backends.memcached.MemcachedCache',
        'pymemcache': 'django.core.cache.backends.memcached.PyLibMCCache',
        'rediscache': 'redis_cache.cache.RedisCache',
        'redis': 'redis_cache.cache.RedisCache',
    }
    _CACHE_BASE_OPTIONS = ['TIMEOUT', 'KEY_PREFIX', 'VERSION', 'KEY_FUNCTION']

    DEFAULT_EMAIL_ENV = 'EMAIL_URL'
    EMAIL_SCHEMES = {
        'smtp': 'django.core.mail.backends.smtp.EmailBackend',
        'smtps': 'django.core.mail.backends.smtp.EmailBackend',
        'consolemail': 'django.core.mail.backends.console.EmailBackend',
        'filemail': 'django.core.mail.backends.filebased.EmailBackend',
        'memorymail': 'django.core.mail.backends.locmem.EmailBackend',
        'dummymail': 'django.core.mail.backends.dummy.EmailBackend'
    }
    _EMAIL_BASE_OPTIONS = ['EMAIL_USE_TLS', ]

    DEFAULT_SEARCH_ENV = 'SEARCH_URL'
    SEARCH_SCHEMES = {
        "elasticsearch": "haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine",
        "solr": "haystack.backends.solr_backend.SolrEngine",
        "whoosh": "haystack.backends.whoosh_backend.WhooshEngine",
        "simple": "haystack.backends.simple_backend.SimpleEngine",
    }
    RESERVED_PATTERN = re.compile('key|secret|passwd|password')



    def __init__(self, init=None, **schema):
        if init is None:
            init = os.environ
        self.__dict__['_environ'] = init
        self.__dict__['_schema'] = schema
        self.__dict__['_resolved'] = None

    def __call__(self, var, cast=None, default=NOTSET):
        return self.get_value(var, cast=cast, default=default)

    # Shortcuts

    def str(self, var, default=NOTSET):
        """
        :rtype: str
        """
        return self.get_value(var, default=default)

    def unicode(self, var, default=NOTSET):
        """Helper for python2
        :rtype: unicode
        """
        return self.get_value(var, cast=text_type, default=default)

    ###########################################################################
    #    Dictionary Interface                                                 #
    ###########################################################################
    def __getitem__(self, key):
        return self.get_value(key)

    def __setitem__(self, key, value):
        if self._resolved is not None and is_variable(value):
            del self._resolved
            self._resolved = None
        self._environ[key] = value

    def __delitem__(self, key):
        del self._environ[key]

    def __iter__(self):
        return iter(self._environ)

    def __len__(self):
        return len(self._environ)

    def get(self, key, default=None):
        return self.get_value(key, default=default)

    def copy(self):
        return self.__class__(self._environ.copy(), **self._schema)

    def keys(self):
        return self._environ.keys()
    ###########################################################################

    __getattr__ = __getitem__

    def __setattr__(self, key, val):
        if key in self.__dict__ or key[:2] == '__':
            self.__dict__[key] = val
        else:
            self.__setitem__(key, val)

    def __getattr__(self, key):
        if key[:2] != '__':
            try:
                return self.__getitem__(key)
            except KeyError:
                pass
        raise AttributeError(key)

    def __delattr__(self, key):
        try:
            del self.__dict__[key]
        except KeyError:
            del self._environ[key]

    def bool(self, var, default=NOTSET):
        """
        :rtype: bool
        """
        return self.get_value(var, cast=bool, default=default)

    def int(self, var, default=NOTSET):
        """
        :rtype: int
        """
        return self.get_value(var, cast=int, default=default)

    def float(self, var, default=NOTSET):
        """
        :rtype: float
        """
        return self.get_value(var, cast=float, default=default)

    def json(self, var, default=NOTSET):
        """
        :returns: Json parsed
        """
        return self.get_value(var, cast=json.loads, default=default)

    def list(self, var, cast=None, default=NOTSET):
        """
        :rtype: list
        """
        return self.get_value(var, cast=list if not cast else [cast], default=default)

    def dict(self, var, cast=dict, default=NOTSET):
        """
        :rtype: dict
        """
        return self.get_value(var, cast=cast, default=default)

    def url(self, var, default=NOTSET):
        """
        :rtype: urlparse.ParseResult
        """
        return self.get_value(var, cast=urlparse.urlparse, default=default)

    def db_url(self, var=DEFAULT_DATABASE_ENV, default=NOTSET, engine=None):
        """Returns a config dictionary, defaulting to DATABASE_URL.

        :rtype: dict
        """
        return self.db_url_config(self.get_value(var, default=default), engine=engine)
    db=db_url

    def cache_url(self, var=DEFAULT_CACHE_ENV, default=NOTSET, backend=None):
        """Returns a config dictionary, defaulting to CACHE_URL.

        :rtype: dict
        """
        return self.cache_url_config(self.url(var, default=default), backend=backend)
    cache=cache_url

    def email_url(self, var=DEFAULT_EMAIL_ENV, default=NOTSET, backend=None):
        """Returns a config dictionary, defaulting to EMAIL_URL.

        :rtype: dict
        """
        return self.email_url_config(self.url(var, default=default), backend=backend)

    def search_url(self, var=DEFAULT_SEARCH_ENV, default=NOTSET, engine=None):
        """Returns a config dictionary, defaulting to SEARCH_URL.

        :rtype: dict
        """
        return self.search_url_config(self.url(var, default=default), engine=engine)

    def resolved(self):
        if self._resolved is None:
            self._resolved = self.__class__(
                interpolated(self._environ), **self._schema
            )
        return self._resolved

    def get_value(self, var, cast=None, default=NOTSET):
        """Return value for given environment variable.

        :param var: Name of variable.
        :param cast: Type to cast return value as.
        :param default: If var not present in environ, return this instead.

        :returns: Value from environment or default (if set)
        """
        logger.debug("get '{0}' casted as '{1}' with default '{2}'".format(var, cast, default))
        try:
            var_info = self._schema[var]
        except KeyError:
            pass
        else:
            try:
                has_default = len(var_info) == 2
            except TypeError:
                has_default = False
            if has_default:
                if not cast:
                    cast = var_info[0]

                if default is self.NOTSET:
                    try:
                        default = var_info[1]
                    except IndexError:
                        pass
            else:
                if not cast:
                    cast = var_info
        try:
            value = self._environ[var]
        except KeyError:
            if default is self.NOTSET:
                #error_msg = "Set the {0} environment variable".format(var)
                raise
            value = default
        if value is not default:
            value = self.parse_value(value, cast)
        if value and is_variable(value):
            try:
                return self.resolved()._environ[var]
            except KeyError:
                pass
        return value

    # Class and static methods

    def parse_value(self, value, cast):
        """Parse and cast provided value

        :param value: Stringed value.
        :param cast: Type to cast return value as.

        :returns: Casted value
        """
        if value is None:
            return value
        elif cast is None:
            return value
        elif cast is bool:
            try:
                value = int(value) != 0
            except ValueError:
                value = value.lower() in self.BOOLEAN_TRUE_STRINGS
        elif isinstance(cast, list):
            value = list(map(cast[0], [x for x in value.split(',') if x]))
        elif isinstance(cast, dict):
            key_cast = cast.get('key', str)
            value_cast = cast.get('value', text_type)
            value_cast_by_key = cast.get('cast', dict())
            value = dict(map(
                lambda kv: (key_cast(kv[0]), self.parse_value(kv[1], value_cast_by_key.get(kv[0], value_cast))),
                [val.split('=') for val in value.split(';') if val]
            ))
        elif cast is dict:
            value = dict([val.split('=') for val in value.split(',') if val])
        elif cast is list:
            value = [x for x in value.split(',') if x]
        elif cast is float:
            # clean string
            float_str = re.sub(r'[^\d,\.]', '', value)
            # split for avoid thousand separator and different locale comma/dot symbol
            parts = re.split(r'[,\.]', float_str)
            if len(parts) == 1:
                float_str = parts[0]
            else:
                float_str = "{0}.{1}".format(''.join(parts[0:-1]), parts[-1])
            value = float(float_str)
        else:
            value = cast(value)
        return value

    def db_url_config(self, url, engine=None):
        """Pulled from DJ-Database-URL, parse an arbitrary Database URL.
        Support currently exists for PostgreSQL, PostGIS, MySQL and SQLite.

        SQLite connects to file based databases. The same URL format is used, omitting the hostname,
        and using the "file" portion as the filename of the database.
        This has the effect of four slashes being present for an absolute file path:

        >>> from environ import Environment
        >>> Environment.db_url_config('sqlite:////full/path/to/your/file.sqlite')
        {'ENGINE': 'django.db.backends.sqlite3', 'HOST': None, 'NAME': '/full/path/to/your/file.sqlite', 'PASSWORD': None, 'PORT': None, 'USER': None}
        >>> Environment.db_url_config('postgres://uf07k1i6d8ia0v:wegauwhgeuioweg@ec2-107-21-253-135.compute-1.amazonaws.com:5431/d8r82722r2kuvn')
        {'ENGINE': 'django.db.backends.postgresql_psycopg2', 'HOST': 'ec2-107-21-253-135.compute-1.amazonaws.com', 'NAME': 'd8r82722r2kuvn', 'PASSWORD': 'wegauwhgeuioweg', 'PORT': 5431, 'USER': 'uf07k1i6d8ia0v'}

        """
        if not isinstance(url, self.URL_CLASS):
            if url == 'sqlite://:memory:':
                # this is a special case, because if we pass this URL into
                # urlparse, urlparse will choke trying to interpret "memory"
                # as a port number
                return {
                    'ENGINE': self.DB_SCHEMES['sqlite'],
                    'NAME': ':memory:'
                }
                # note: no other settings are required for sqlite
            url = urlparse.urlparse(url)

        config = {}

        # Remove query strings.
        path = url.path[1:]
        path = path.split('?', 2)[0]

        # if we are using sqlite and we have no path, then assume we
        # want an in-memory database (this is the behaviour of sqlalchemy)
        if url.scheme == 'sqlite' and path == '':
            path = ':memory:'
        if url.scheme == 'ldap':
            path = '{scheme}://{hostname}'.format(scheme=_cast_str(url.scheme), hostname=_cast_str(url.hostname))
            if url.port:
                path += ':{port}'.format(port=_cast_str(url.port))

        # Update with environment configuration.
        config.update({
            'NAME': path,
            'USER': _cast_str(url.username),
            'PASSWORD': _cast_str(url.password),
            'HOST': _cast_str(url.hostname),
            'PORT': _cast_int(url.port),
        })

        if url.query:
            config_options = {}
            for k, v in urlparse.parse_qs(url.query).items():
                if k.upper() in self._DB_BASE_OPTIONS:
                    config.update({k.upper(): _cast_int(v[0])})
                else:
                    config_options.update({k: _cast_int(v[0])})
            config['OPTIONS'] = config_options

        if engine:
            config['ENGINE'] = engine
        if url.scheme in Environment.DB_SCHEMES:
            config['ENGINE'] = Environment.DB_SCHEMES[url.scheme]

        if not config.get('ENGINE', False):
            warnings.warn("Engine not recognized from url: {0}".format(config))
            return {}

        return config

    def cache_url_config(self, url, backend=None):
        """Pulled from DJ-Cache-URL, parse an arbitrary Cache URL.

        :param url:
        :param overrides:
        :return:
        """
        url = urlparse.urlparse(url) if not isinstance(url, self.URL_CLASS) else url

        location = url.netloc.split(',')
        if len(location) == 1:
            location = location[0]

        config = {
            'BACKEND': self.CACHE_SCHEMES[url.scheme],
            'LOCATION': location,
        }

        if url.scheme == 'filecache':
            config.update({
                'LOCATION': _cast_str(url.netloc + url.path),
            })

        if url.path and url.scheme in ['memcache', 'pymemcache', 'rediscache']:
            config.update({
                'LOCATION': 'unix:' + url.path,
            })

        if url.query:
            config_options = {}
            for k, v in urlparse.parse_qs(url.query).items():
                opt = {k.upper(): _cast_int(v[0])}
                if k.upper() in self._CACHE_BASE_OPTIONS:
                    config.update(opt)
                else:
                    config_options.update(opt)
            config['OPTIONS'] = config_options

        if backend:
            config['BACKEND'] = backend

        return config

    def email_url_config(self, url, backend=None):
        """Parses an email URL."""

        config = {}

        url = urlparse.urlparse(url) if not isinstance(url, self.URL_CLASS) else url

        # Remove query strings
        path = url.path[1:]
        path = path.split('?', 2)[0]

        # Update with environment configuration
        config.update({
            'EMAIL_FILE_PATH': path,
            'EMAIL_HOST_USER': _cast_str(url.username),
            'EMAIL_HOST_PASSWORD': _cast_str(url.password),
            'EMAIL_HOST': _cast_str(url.hostname),
            'EMAIL_PORT': _cast_int(url.port),
        })

        if backend:
            config['EMAIL_BACKEND'] = backend
        elif url.scheme in self.EMAIL_SCHEMES:
            config['EMAIL_BACKEND'] = self.EMAIL_SCHEMES[url.scheme]

        if url.scheme == 'smtps':
            config['EMAIL_USE_TLS'] = True
        else:
            config['EMAIL_USE_TLS'] = False

        if url.query:
            config_options = {}
            for k, v in urlparse.parse_qs(url.query).items():
                opt = {k.upper(): _cast_int(v[0])}
                if k.upper() in self._EMAIL_BASE_OPTIONS:
                    config.update(opt)
                else:
                    config_options.update(opt)
            config['OPTIONS'] = config_options

        return config

    def search_url_config(self, url, engine=None):
        config = {}

        url = urlparse.urlparse(url) if not isinstance(url, self.URL_CLASS) else url

        # Remove query strings.
        path = url.path[1:]
        path = path.split('?', 2)[0]

        if url.scheme in self.SEARCH_SCHEMES:
            config["ENGINE"] = self.SEARCH_SCHEMES[url.scheme]

        if path.endswith("/"):
            path = path[:-1]

        split = path.rsplit("/", 1)

        if len(split) > 1:
            path = split[:-1]
            index = split[-1]
        else:
            path = ""
            index = split[0]

        config.update({
            "URL": urlparse.urlunparse(("http",) + url[1:2] + (path,) + url[3:]),
            "INDEX_NAME": index,
            })

        if path:
            config.update({
                "PATH": path,
            })

        if engine:
            config['ENGINE'] = engine

        return config

    def read_env(self, env_file=None, **overrides):
        """Read a .env file into os.environ.

        If not given a path to a dotenv path, does filthy magic stack backtracking
        to find manage.py and then find the dotenv.

        http://www.wellfireinteractive.com/blog/easier-12-factor-django/

        https://gist.github.com/bennylope/2999704
        """
        if env_file is None:
            frame = sys._getframe()
            env_file = os.path.join(os.path.dirname(frame.f_back.f_code.co_filename), '.env')
            if not os.path.exists(env_file):
                warnings.warn("not reading %s - it doesn't exist." % env_file)
                return

        def iterator(iterable):
            for line in iterable:
                m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
                if m1:
                    key, val = m1.group(1), m1.group(2)
                    m2 = re.match(r"\A'(.*)'\Z", val)
                    if m2:
                        val = m2.group(1)
                    m3 = re.match(r'\A"(.*)"\Z', val)
                    if m3:
                        val = re.sub(r'\\(.)', r'\1', m3.group(1))
                    yield key, text_type(val)

        self.read(env_file, overrides=overrides, iterator=iterator)

    def read(self, files, defaults=None, overrides=None, iterator=None):
        """
        Populate the environment dictionary from one or more files.

        Interpolates values in the format $var or ${var}. If an interpolation
        target is missing, a KeyError is raised; and if any key is an invalid
        Python variable, a ValueError is raised.

        The default file iterator will determine key/value pairs by splitting
        lines on both '=' and ':='.
        """
        if isinstance(files, basestring) or hasattr(files, 'read'):
            files = [files]
        self._environ.update(resolve_files(files, defaults, overrides, iterator))

    def pprint(
        self, stream=sys.stdout, maxlines=-1, safe=False, encoding='utf-8',
        uppercase=False, globs=None):

        def is_reserved(key):
            return bool(self.RESERVED_PATTERN.search(key.lower()))

        def is_wanted(key):
            if not key or key[0] == '_':
                return False
            if uppercase and key.upper() != key:
                return False
            if not globs:
                return True
            for glob in globs:
                if fnmatch(key, glob):
                    return True
            return False

        from itertools import groupby
        env = self._environ
        line = -1 * maxlines
        for _, group in groupby(sorted(env.keys()), lambda X: X.split('_')[0]):
            if line == 0:
                break
            stream.write(b'\n')
            for key in group:
                if line == 0:
                    break
                if not is_wanted(key):
                    continue
                if not safe and is_reserved(key):
                    val = '*'*8
                else:
                    val = env[key]
                stream.write(('%s = %s' % (key, val)).strip().encode(encoding))
                stream.write(b'\n')
                line += 1
        stream.write(b'\n')

environ = Environment()


def register_scheme(scheme):
    for method in filter(lambda s: s.startswith('uses_'), dir(urlparse)):
        getattr(urlparse, method).append(scheme)

# Register database and cache schemes in URLs.
_SCHEMES = []
for schtype in ['DB', 'CACHE', 'SEARCH', 'EMAIL']:
    _SCHEMES.extend(getattr(Environment, schtype + '_SCHEMES').keys())
for schema in _SCHEMES:
    register_scheme(schema)

