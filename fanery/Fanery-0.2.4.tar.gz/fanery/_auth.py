__all__ = ['acl', 'hooks']

from functools import wraps

from _term import Hict, gen_uuid_bytes
from _exc import Unauthorized
import _config as conf

acl_rules = dict(role=lambda s, roles, *args, **argd: s.role in roles and role in s.profile.roles,  # noqa
                 user=lambda s, users, *args, **argd: s.profile.username in users,                  # noqa
                 origin=lambda s, origins, *args, **argd: s.origin in origins,
                 domain=lambda s, domains, *args, **argd: s.domain in domains)


def set_acl_rule(name, func):
    acl_rules[name] = func


def acl(**rules):

    for k, v in rules.iteritems():
        validator = acl_rules.get(k, v)
        assert callable(validator), ('invalid-acl', k)
        rules[k] = (v, validator)

    def decorator(f):

        from _state import get_state

        @wraps(f)
        def wrapper(*args, **argd):
            _state_ = get_state()
            for k, (v, validator) in rules.iteritems():
                try:
                    if v is validator:
                        valid = validator(_state_, *args, **argd)
                    else:
                        valid = validator(_state_, v, *args, **argd)
                except:
                    valid = False

                if valid is True:
                    continue
                elif valid is False:
                    raise Unauthorized(k)
                else:
                    raise Unauthorized(k, valid)

            return f(*args, **argd)

        return wrapper

    return decorator


def _undefined(name):

    def wrapper(*argv, **argd):
        raise NotImplementedError(name)

    return wrapper


def _default(key):
    key = key.upper()

    assert hasattr(conf, key), key

    def _default(*args, **argd):
        return getattr(conf, key)
    _default.is_default = True

    return _default

hooks = Hict(load_state=_undefined('hooks.load_state'),
             store_state=_undefined('hooks.store_state'),
             active_user_sessions=_undefined('hooks.active_user_sessions'),
             destroy_user_sessions=_undefined('hooks.destroy_user_sessions'),
             max_active_user_sessions=_default('max_active_user_sessions'),
             fetch_profile=_undefined('hooks.fetch_profile'),
             has_permission=_undefined('hooks.has_permission'),
             store_prelogin=_undefined('hooks.store_prelogin'),
             incr_abuse=_undefined('hooks.incr_abuse'),
             max_pads_count=_default('max_pads_count'),
             pad_grace_time=_default('pad_grace_time'),
             max_origin_abuse_level=_default('max_origin_abuse_level'),
             abuse_level_watch_period=_default('abuse_level_watch_period'),
             abuse_level_by_origin=_undefined('hooks.abuse_level_by_origin'),
             prelogin_grace_time=_default('prelogin_grace_time'),
             prelogin_count=_undefined('hooks.prelogin_count'),
             max_prelogin_count=_default('max_prelogin_count'),
             session_timeout=_default('session_timeout'),
             gen_session_id=gen_uuid_bytes)

default_settings = tuple(k for k, v in hooks.items()
                         if getattr(v, 'is_default', False))

### Profiles model reference implementation.

from time import time as timestamp

import logging
logger = logging.getLogger('fanery.auth')


class Profile:

    @classmethod
    def initialize(cls, record):
        from _state import get_state
        record.merge(domain=get_state().domain)

    @classmethod
    def validate(cls, record):
        from _term import is_str, is_email, Hict

        errors, dct = Hict(), record._dct

        domain = dct.get('domain')
        if not domain:
            errors.domain.required = domain

        username = dct.get('username')
        if not username:
            errors.username.required = username
        elif not is_str(username):
            errors.username.bad_type = type(username).__name__

        password_hash = dct.get('password_hash')
        if not password_hash:
            errors.password.required = password_hash

        email = dct.get('email')
        if not email:
            errors.email.required = email
        elif not is_str(email):
            errors.email.bad_type = type(email).__name__
        elif not is_email(email):
            errors.email.bad_format = email

        if errors:
            print dct
        return errors

    @classmethod
    def index(cls, record):
        return dict((k, v) for k, v in record._dct.iteritems()
                    if not k.startswith('password_'))


def setup(db):
    from _store import add_model, add_storage

    start = timestamp()
    try:
        add_model(Profile)
        add_storage(db, Profile)
    finally:
        logger.debug('%0.6f setup' % (timestamp() - start))


def add_user(username, password=None, **extra):
    from _crypto import nacl_random
    from _state import get_state
    from _store import storage
    from _term import is_str
    from _auth import hooks
    from scrypt import hash

    start = timestamp()
    try:
        state = get_state()
        domain = state.domain = extra.setdefault('domain', state.domain)
        extra.setdefault('email', '%s@%s' % (username, 'example.com'))

        user = hooks.fetch_profile(domain, username)
        if user is None:
            if not password:
                password = nacl_random(16).encode('hex')
            else:
                assert is_str(password), 'bad-type'

            salt = nacl_random(16)
            password_hash = hash(password, salt)

            desc = "adduser %s:%s@%s" % (username, password, domain)
            with storage(desc) as db:
                db.insert(Profile,
                          username=username,
                          password_hash=password_hash,
                          password_salt=salt,
                          **extra)
    finally:
        logger.debug('%0.6f init' % (timestamp() - start))
