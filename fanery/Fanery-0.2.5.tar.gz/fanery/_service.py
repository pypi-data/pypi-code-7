__all__ = ['service', 'static']

from _term import (
    Hict, is_str, to_str,
    parse_term, parse_json,
    to_simple, to_json,
)
from _crypto import (
    nacl_box, nacl_sign, nacl_verify,
    nacl_nonce, nacl_random, nacl_sha256,
    PrivateKey, PublicKey, Box, SigningKey
)
from _autoreload import observe_module
from _auth import hooks as auth
from _state import get_state
import _config as conf
import _exc as exc

from os.path import splitext, normpath, realpath, isdir, isfile, join
from base64 import b64encode, b64decode
from time import time as timestamp
from functools import wraps
from sys import exc_info
from cxor import xor

import logging
logger = logging.getLogger('fanery.service')

try:
    import ipdb as pdb
except ImportError:
    import pdb

try:
    import xtraceback
    traceback = xtraceback.compat
    traceback.install_traceback()
    traceback.install_sys_excepthook()
except ImportError:
    import traceback


# services registry -> see service() and lookup()
registry = dict()


def is_abusive(domain, origin):
    max_abuse_level = auth.max_origin_abuse_level(domain)
    if max_abuse_level > 0:
        origin_abuse_level = auth.abuse_level_by_origin(origin, domain)
        return bool(origin_abuse_level >= max_abuse_level)


def decrypt(keys, sign, pad=None):
    enc = nacl_verify(sign, keys.vkey)
    box, _, _ = nacl_box(keys.ckey, keys.skey)
    msg = box.decrypt(xor(enc, pad) if pad else enc)
    return box, parse_json(msg)


def encrypt(state, box, term, pad=None):
    enc = box.encrypt(to_json(to_simple(term)), nacl_nonce())
    assert not pad or len(enc) <= len(pad), 'short-pad'
    sign = nacl_sign(xor(enc, pad) if pad else enc, state.sseed)[0]
    return Hict(sign=b64encode(sign))


def service(urlpath=None, auto_parse=True, static=False, accel=False,
            cache=False, force_download=False, content_disposition=False,
            auto_close_file=True, check_abusive=True, check_perm=True,
            postmortem_debug=False, force_define=False, log_exc=True,
            use_one_time_pad=True, safe=True, ssl=None, csp=None,
            **output):

    for k, v in output.iteritems():
        if not (k and k.isalnum() and callable(v)):
            raise exc.InvalidOutputFormatter(k, v)
    else:
        output.setdefault('json', lambda t: to_json(to_simple(t)))
        output.setdefault('txt', lambda t: to_str(to_simple(t)))
        output.setdefault('raw', repr)

    if not safe:
        use_one_time_pad = False

    if content_disposition is True:
        force_download = False
    elif force_download is True:
        content_disposition = False

    def decorator(f):
        srv_path = (urlpath or f.__name__).strip('/')

        if srv_path in registry:
            if force_define is True or conf.IS_DEVELOPMENT:
                logger.debug("redefine <%s> for %s() in %s line %d" % (
                    srv_path,
                    f.func_code.co_name,
                    f.func_code.co_filename,
                    f.func_code.co_firstlineno))
            else:
                raise exc.MultipleDefine(srv_path)
        elif conf.IS_DEVELOPMENT:
            observe_module(f)

        @wraps(f)
        def wrapper(*args, **argd):

            _state_ = get_state()

            if ssl is not False and (not conf.IS_DEVELOPMENT or ssl) and not _state_.ssl:   # noqa
                raise exc.RequireSSL(srv_path)

            domain = _state_.domain
            origin = _state_.origin

            if check_abusive and is_abusive(domain, origin):
                raise exc.Abusive(origin)

            if safe is True:

                sid = b64decode(argd.pop('sid', ''))
                if not sid:
                    auth.incr_abuse(origin, domain,
                                    abuse=('sid', None, srv_path))
                    raise exc.Unauthorized

                stored = auth.load_state(domain, sid)
                if not stored:
                    auth.incr_abuse(origin, domain,
                                    abuse=('sid', sid, srv_path))
                    raise exc.UnknownSession
                elif stored.expires <= timestamp():
                    raise exc.ExpiredSession
                else:
                    _state_.update(stored)
                    _state_.origin = origin

                if check_perm and not auth.has_permission(_state_, srv_path):
                    auth.incr_abuse(origin, domain, incr=3,
                                    abuse=('auth', sid, srv_path))
                    raise exc.Unauthorized

                sign = b64decode(argd.pop('sign', ''))
                if not sign:
                    auth.incr_abuse(origin, domain, incr=3,
                                    abuse=('sign', sid, srv_path))
                    raise exc.InvalidCall('sign')

                if use_one_time_pad is True:
                    pid, pads = b64decode(argd.pop('pid', '')), stored.pads
                    cpads = pads.get(srv_path, None)
                    if not pid or not cpads or pid not in cpads:
                        auth.incr_abuse(origin, domain, incr=3,
                                        abuse=('pid', sid, srv_path))
                        raise exc.InvalidCall('pid')

                    keys = cpads.pop(pid)
                    pad = keys.pad
                    if not cpads:
                        del pads[srv_path]
                else:
                    keys = _state_
                    pad = None

                try:
                    box, term = decrypt(keys, sign, pad)
                except:
                    auth.incr_abuse(origin, domain, incr=3,
                                    abuse=('pad', sid, srv_path))
                    raise exc.InvalidCall('pad')

                argd.update(term)

            if auto_parse is True:
                args = parse_term(args) if args else args
                argd = parse_term(argd) if argd else argd

            try:
                _state_.service = srv_path

                if not use_one_time_pad and safe is True:
                    ret = f(box, *args, **argd)
                else:
                    ret = f(*args, **argd)

                if safe is True:
                    if _state_.expires > 0:
                        _state_.expires = timestamp() + auth.session_timeout(domain)    # noqa
                        auth.store_state(_state_)
                    else:
                        auth.destroy_state(_state_)

            except Exception:

                exc_type, exc_value, exc_traceback = exc_info()

                if postmortem_debug is True:
                    traceback.print_exc()
                    pdb.post_mortem(exc_traceback)
                elif log_exc is True:
                    logger.error(srv_path, exc_info=True)

                if safe is True:
                    ret = dict(low=isinstance(exc_type, (AssertionError, exc.FaneryException)), # noqa
                               exc=exc_type.__name__, err=to_simple(exc_value.args))            # noqa
                    _state_.error.update(ret)
                else:
                    raise

            if use_one_time_pad is True:
                return encrypt(keys, box, ret)
            else:
                return ret

        wrapper.csp = csp
        wrapper.ssl = ssl
        wrapper.safe = safe
        wrapper.cache = cache
        wrapper.static = static
        wrapper.output = output
        wrapper.urlpath = srv_path
        wrapper.auto_parse = auto_parse
        wrapper.force_download = force_download
        wrapper.auto_close_file = auto_close_file
        wrapper.content_disposition = content_disposition
        wrapper.accel = accel.lower() if is_str(accel) else None

        registry[srv_path] = wrapper

        return wrapper

    return decorator


def lookup(urlpath, full=None, max_recursion=5, max_urlpath_args=5):

    path, ext = splitext(urlpath.strip().strip('/'))
    args = []

    while path not in registry and len(args) <= max_urlpath_args:
        try:
            path, arg = path.strip().rsplit('/', 1)
            args.append(arg.strip())
        except ValueError:
            break

    fun = registry.get(path, None)

    if not fun and max_recursion > 0:
        try:
            prefix, urlpath = urlpath.split('/', 1)
            return lookup(urlpath, full or urlpath, max_recursion - 1)
        except ValueError:
            fun = registry.get('', None)
            args = [full]
    elif args:
        args.reverse()
        if fun and fun.static is True:
            args[-1] += ext

    out = fun.output.get(ext[1:], False) if ext and fun else None

    return fun, args, ext, out


def consume(_state_, service_call, *args, **argd):
    start = timestamp()
    try:
        fun = error = exception = None

        if isinstance(service_call, basestring):
            urlpath = service_call
            fun, argv, ext, out = lookup(normpath(service_call))
        else:
            urlpath, fun, argv, ext, out = service_call

        if not callable(fun):
            raise exc.NotFound(urlpath)

        if ext and not (fun.static or callable(out)):
            raise exc.UndefinedOutputFormatter(urlpath)

        argv.extend(args)
        ret = fun(*argv, **argd)

        return fun, ext, out(ret) if ext and out else ret
    except exc.FaneryException, error:
        raise
    except Exception, exception:
        raise
    finally:
        sid, profile = _state_.sid, _state_.profile
        msg = "%s %s %s %s %s %s %s %s %0.6f %s" % (
            'S' if _state_.ssl else '-',
            'A' if fun and fun.auto_parse else '-',
            'S' if fun and fun.static else '-',
            _state_.origin, _state_.domain,
            sid.encode('hex') if sid else '-',
            profile.username if profile else '-',
            _state_.role or '-',
            timestamp() - start,
            urlpath)

        if _state_.error:
            logger.error("%s [%s]" % (msg, _state_.error.exc))
        elif error:
            logger.warning("%s [%s]" % (msg, error.__class__.__name__))
        elif exception:
            logger.error("%s [%s]" % (msg, exception.__class__.__name__))
        else:
            logger.info(msg)


def static(urlpath, root, index='index.html', **argd):

    root = join(realpath(normpath(root)), '')
    if not isdir(root):
        raise exc.NotFound(root)

    argd.setdefault('cache', True)
    argd.setdefault('log_exc', False)
    argd.setdefault('csp', "default-src 'self' 'unsafe-eval'")

    @service(urlpath, auto_parse=False, static=True, safe=False, **argd)
    def serve_file(*args, **argd):
        filepath = realpath(normpath(join(root, *args)))

        if isdir(filepath):
            if index:
                filepath = join(filepath, index)
            elif filepath.startswith(root):
                return filepath
            else:
                raise exc.NotFound(join(*args or [index]))

        if isfile(filepath) and filepath.startswith(root):
            return filepath
        else:
            raise exc.NotFound(join(*args or [index]))

    return serve_file


static(conf.JFANERY_URLPATH, conf.JFANERY_DIRPATH)


@service('fanery/prelogin', ssl=False, safe=False, auto_parse=False, log_exc=False)             # noqa
def prelogin(identity, **extra):
    state = get_state()
    origin = state.origin
    domain = state.domain

    max_count = auth.max_prelogin_count(domain)
    prelogin_count = auth.prelogin_count(domain, origin)
    if max_count <= 0 or prelogin_count < max_count:

        profile = auth.fetch_profile(domain, identity, **extra)
        if profile is not None:
            sid = auth.gen_session_id()
            hash = profile.password_hash
            ckey = PrivateKey(nacl_sha256(hash))
            skey = PrivateKey.generate()
            sseed = nacl_random(32)
            cseed = nacl_random(32)

            box = Box(skey, ckey.public_key)
            csign = SigningKey(cseed)
            sign = csign.sign(hash)[:64]
            pad = nacl_random(len(sign))
            sign = xor(sign, pad)

            auth.store_prelogin(expires=timestamp() + auth.prelogin_grace_time(domain),         # noqa
                                sid=sid, domain=domain, origin=origin,
                                identity=identity, sign=sign,
                                profile=profile._uuid,
                                ckey=ckey.public_key.encode(),
                                vkey=csign.verify_key.encode(),
                                skey=skey.encode(), sseed=sseed)

            vkey = SigningKey(sseed).verify_key.encode()
            enc = box.encrypt(cseed + vkey + sid + pad, nacl_nonce())
            return Hict(pkey=b64encode(skey.public_key.encode()),
                        salt=b64encode(profile.password_salt),
                        enc=b64encode(enc))
        else:
            auth.incr_abuse(origin, domain, abuse=('prelogin', identity))

    # do not tell directly prelogin attempt was unsuccessful
    # let the client waste time trying to decrypt some garbage
    return Hict(pkey=b64encode(PrivateKey.generate().public_key.encode()),
                salt=b64encode(nacl_random(8)),
                enc=b64encode(nacl_random(184)))


@service('fanery/login', ssl=False, safe=False, auto_parse=False, log_exc=False)                # noqa
def login(identity, sid, sign, force=False):
    state = get_state()
    origin = state.origin
    domain = state.domain

    sign = b64decode(sign)
    sid = b64decode(sid)

    prelogin = auth.fetch_prelogin(origin, domain, sid)
    profile = auth.fetch_profile(domain, identity) if prelogin else None

    if not profile or not prelogin or timestamp() >= prelogin.expires:
        auth.incr_abuse(origin, domain, abuse=('login', identity))
    elif prelogin.profile != profile._uuid or prelogin.sign != sign:
        auth.incr_abuse(origin, domain, incr=3, abuse=('sign', identity))
    else:
        max_sessions = auth.max_active_user_sessions(domain, identity)
        if max_sessions > 0:
            active_sessions = auth.active_user_sessions(domain, identity)
            if not force and active_sessions >= max_sessions:
                raise exc.MaxActiveSessions
            elif force:
                auth.destroy_user_sessions(domain, identity)

        box = Box(PrivateKey(prelogin.skey), PublicKey(prelogin.ckey))
        skey = PrivateKey.generate()
        ckey = PrivateKey.generate()
        expires = timestamp() + auth.session_timeout(domain)

        state.update(sid=sid, profile=profile, expires=expires,
                     ckey=ckey.public_key.encode(), skey=skey.encode(),
                     sseed=prelogin.sseed, vkey=prelogin.vkey)
        auth.store_state(state)

        tstamp = str(int(timestamp()))
        msg = ckey.encode() + skey.public_key.encode() + tstamp
        enc = box.encrypt(msg, nacl_nonce())
        sign = SigningKey(prelogin.sseed).sign(enc)
        return Hict(sign=b64encode(sign))

    raise exc.InvalidCredential


@service('fanery/gen_pad', ssl=False, use_one_time_pad=False, auto_parse=False, log_exc=False)  # noqa
def gen_pad(box, call, pad, tstamp):
    state = get_state()

    if not state.profile:
        raise exc.Unauthorized

    try:
        tsdiff = timestamp() - float(tstamp)
    except:
        raise exc.InvalidCall

    domain = state.domain
    pads = state.pads

    if abs(tsdiff) > auth.pad_grace_time(domain, call):
        auth.incr_abuse(state.origin, domain, abuse=('timeout', call))
        raise exc.CallPadTimeout(dict(tsdiff=tsdiff))
    elif not auth.has_permission(state, call):
        auth.incr_abuse(state.origin, domain, abuse=('denied', call))
        raise exc.Unauthorized
    elif call in pads and len(pads[call]) >= auth.max_pads_count(domain, call):
        auth.incr_abuse(state.origin, domain, abuse=('pads', call))
        raise exc.CallPadsLimitExceeded

    # gen one-time-pad and one-time-keys
    cid = nacl_random(16)
    cseed = nacl_random(32)
    sseed = nacl_random(32)
    skey = PrivateKey.generate()
    ckey = PrivateKey.generate()

    # server call pad data
    pad = b64decode(pad)
    size = len(pad) - 410
    cvkey = SigningKey(cseed).verify_key
    cpad = pads[call][cid] = Hict(pad=nacl_random(size), call=call,
                                  skey=skey.encode(), sseed=sseed,
                                  ckey=ckey.public_key.encode(),
                                  vkey=cvkey.encode())

    # client pad data
    svkey = SigningKey(sseed).verify_key
    data = Hict(pad=b64encode(cpad.pad),
                pid=b64encode(cid),
                cseed=b64encode(cseed),
                ckey=b64encode(ckey.encode()),
                skey=b64encode(skey.public_key.encode()),
                vkey=b64encode(svkey.encode()))

    return encrypt(state, box, data, pad)


@service('fanery/logout', ssl=False, auto_parse=False, log_exc=False)
def logout(*args, **argd):
    _state_ = get_state()
    _state_.expires = 0
    return True
