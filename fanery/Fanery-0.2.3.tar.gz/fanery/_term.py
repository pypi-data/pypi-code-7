from inspect import (  # noqa
    ismodule as is_module,
    isfunction as is_function,
    isgenerator as is_generator,
    isbuiltin as is_builtin,
    isclass as is_class
)

from datetime import datetime, date
from collections import Iterable
from decimal import Decimal
from uuid import UUID
from os import path


class Hict(dict):
    """
    Hierarchical dotted dictionary.
    """

    def __missing__(self, key):
        term = self[key] = Hict()
        return term

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def is_str(term):
    return isinstance(term, basestring)


def is_number(term):
    return isinstance(term, (int, long, float, Decimal))


def is_date(term):
    return isinstance(term, (date, datetime))


def is_uuid(term):
    return isinstance(term, UUID)


def is_sequence(term):
    return hasattr(term, '__iter__') \
        and not isinstance(term, (basestring, dict)) \
        and not is_generator(term)


def is_dict(term):
    return isinstance(term, dict) or type(term) is dict


def is_inet_address(term):
    raise NotImplementedError


def is_inet6_address(term):
    raise NotImplementedError


def is_file_path(term):
    try:
        return path.isfile(term)
    except:
        return False


def is_dir_path(term):
    try:
        return path.isdir(term)
    except:
        return False


try:
    from libuuid import uuid4 as gen_uuid, uuid4_bytes as gen_uuid_bytes   # noqa
except ImportError:
    from uuid import uuid4 as gen_uuid      # noqa

    def gen_uuid_bytes():
        return gen_uuid().bytes


from re import compile as regex
try:
    from validate_email import validate_email as is_email
except ImportError:
    from email.utils import parseaddr as _parse_email_addr
    # borrowed from http://www.regular-expressions.info/email.html
    _email_regex = regex(r'''[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?''')  # noqa

    def is_email(term, verify=False):
        try:
            name, email = _parse_email_addr(term)
            return _email_regex.match(email)
        except:
            return False


def to_str(term):
    #FIXME: handle any term
    return '%s' % term


def to_simple(term):
    if not term or isinstance(term, (int, float, basestring)):
        return term
    elif isinstance(term, dict) or type(term) is dict:
        return dict((to_simple(k), to_simple(v))
                    for k, v in term.iteritems())
    elif isinstance(term, Iterable):
        return [to_simple(t) for t in term]
    else:
        return str(term)


try:
    from ciso8601 import parse_datetime
except ImportError:
    try:
        import arrow

        def parse_datetime(term):
            return arrow.get(term).datetime
    except ImportError:
        def parse_datetime(term):
            return datetime.strptime(term, "%Y-%m-%dT%H:%M:%S.%f")


def parse_term(term, dict_type=dict, parse_dict_key=False):
    if term and isinstance(term, basestring):
        try:
            f = float(term)
            i = int(f)
            if i == f:
                return i
            elif str(f) == term:
                return f
            else:
                return Decimal(term)
        except:
            pass
        try:
            return UUID(term)
        except:
            pass
        try:
            dt = parse_datetime(term)
            return dt if dt.time() else dt.date()
        except:
            return term
    elif isinstance(term, dict) or type(term) is dict:
        if parse_dict_key is True:
            return dict_type((parse_term(k, dict_type, parse_dict_key),
                              parse_term(v, dict_type, parse_dict_key))
                             for k, v in term.iteritems())
        else:
            return dict_type((k, parse_term(v, dict_type, parse_dict_key))
                             for k, v in term.iteritems())
    elif is_sequence(term):
        return type(term)(parse_term(t, dict_type, parse_dict_key) for t in term)   # noqa
    else:
        return term


try:
    from msgpack import packb as to_msgpack, unpackb as parse_msgpack
except ImportError:
    from umsgpack import packb as to_msgpack, unpackb as parse_msgpack
finally:
    from base64 import b64encode, b64decode

    def dump_term(term, **argd):
        argd.setdefault('use_bin_type', True)
        return b64encode(to_msgpack(to_simple(term), **argd))

    def load_term(encoded, **argd):
        encoding = argd.pop('encoding', 'utf-8')
        term = parse_msgpack(b64decode(encoded), encoding=encoding)
        return parse_term(term, **argd)


try:
    from ujson import dumps as to_json, loads as parse_json
except ImportError:
    try:
        from yajl import Encoder, Decoder
        parse_json = Decoder().decode
        to_json = Encoder().encode
    except ImportError:
        try:
            from jsonlib import write as to_json, read as parse_json
        except ImportError:
            try:
                from cjson import encode as to_json, decode as parse_json
            except ImportError:
                try:
                    from simplejson import dumps as to_json, loads as parse_json  # noqa
                except ImportError:
                    from json import dumps as to_json, loads as parse_json        # noqa


from unicodedata import normalize as _normalize
_punct_regex = regex(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')
_file_punct_regex = regex(r'[\t !"#$%&\'*/<=>?@\[\\\]^`{|}:]+')


def normalize_filename(term, mode='NFKD'):
    assert isinstance(term, basestring), 'bad-type: %r' % term
    text = ' '.join(_file_punct_regex.split(path.basename(term)))
    return _normalize(mode, text).encode('ascii', 'ignore')


def normalize(term, mode='NFKD'):
    assert isinstance(term, basestring), 'bad-type: %r' % term
    text = ' '.join(_punct_regex.split(term))
    return _normalize(mode, text).encode('ascii', 'ignore')


def slugify(term, delim='-'):
    return normalize(term).lower().replace(' ', delim)
