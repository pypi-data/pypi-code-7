"""
Handle sessions in execution stack.
"""
__all__ = ['get_state']

from time import time as timestamp
from inspect import currentframe

from _auth import hooks as auth
from _term import Hict
import _exc as exc


class State(Hict):
    pass


def new_state(domain='localhost', **data):
    default = Hict(origin='127.0.0.1', domain=domain, service=None,
                   expires=timestamp() + auth.session_timeout(domain),
                   impersonated_by=None, profile=None,
                   sid=auth.gen_session_id())
    default.update(data)
    return State(default)


def get_state(**data):
    frame = caller = currentframe().f_back
    while frame:
        _state_ = frame.f_locals.get('_state_', None)
        if not _state_:
            frame = frame.f_back
            continue
        elif caller is not frame:
            caller.f_locals['_state_'] = _state_
        break
    else:
        _state_ = new_state(**data)
        caller.f_locals['_state_'] = _state_
    return _state_


def load_state(sid, **data):
    _state_ = auth.load_state(sid)
    if _state_:
        if _state_.expires > timestamp():
            _state_.profile = auth.fetch_profile(_state_.profile)
        else:
            raise exc.SessionTimeout
    else:
        _state_ = new_state()
        store_state(_state_)
    return _state_


def store_state(state):
    state.expires = timestamp() + auth.session_timeout(state.domain)
    state = State(state)
    state.profile = getattr(state.profile, '_uuid', None)
    auth.store_state(state)


def clear_state(state):
    state.data.clear()
    state.expires = 0
