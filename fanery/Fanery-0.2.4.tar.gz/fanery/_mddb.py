"""
Toy in-memory storage implementation.
"""

from collections import defaultdict
from time import time as timestamp
from _auth import hooks
from _term import Hict


class MemDictStore(object):

    def __init__(self):
        self._prelogins = defaultdict(dict)
        self._abuses = defaultdict(list)
        self._models = dict()
        self._sessions = dict()

    def do_nothing(self, *args, **argd):
        pass
    begin = commit = rollback = do_nothing

    def add_model(self, model, add_index):
        self._models[model] = dict()

    def store(self, domain, txn, inserts=None, updates=None, deletes=None):
        if inserts:
            self.upsert(domain, txn, inserts)
        if updates:
            self.upsert(domain, txn, updates)
        if deletes:
            self.delete(domain, txn, deletes)

    def upsert(self, domain, txn, records):
        for record in records:
            self._models[record._model][record._uuid] = record
    insert = update = upsert

    def delete(self, domain, txn, records):
        for record in records:
            del self._models[record._model][record._uuid]

    def fetch(self, domain, model, uuid, vsn=None, txn=None):
        record = self._models[model][uuid]
        assert not vsn or record._vsn == vsn
        assert not txn or record._txn == txn
        return record._vsn, record._txn, record._dct

    def query(self, domain, model, fun=None, score=None):
        for record in filter(fun or (lambda r: True),
                             self._models[model].itervalues()):
            uuid, vsn, txn = record._uuid, record._vsn, record._txn
            if score is not None:
                yield (uuid, vsn, txn, score)
            else:
                yield (uuid, vsn, txn)

    def search(self, domain, model, fun):
        return self.query(domain, model, fun, 1)

    def select(self, domain, model, fun=None):
        return self.query(domain, model, fun)

    def find(self, domain, model, terms):
        for record in self._models[model].itervalues():
            if record.domain == domain:
                dct = record._dct
                for k, v in terms.iteritems():
                    if k in dct and dct[k] == v:
                        continue
                    else:
                        break
                else:
                    return record

    def fetch_profile(self, domain, identity, **extra):
        extra.update(username=identity)
        return self.find(domain, 'Profile', extra)

    def has_permission(self, state, call):
        return True

    def active_user_sessions(self, domain, identity):
        now = timestamp()
        return sum(s.expires > now
                   and s.domain == domain
                   and s.identity == identity
                   for s in self._sessions.itervalues())

    def destroy_sessions(self, domain, identity):
        sessions = self._sessions
        for sid, s in sessions.iteritems():
            if s.domain == domain and s.identity == identity:
                del sessions[sid]

    def load_state(self, domain, sid):
        return self._sessions.get(sid, None)

    def store_state(self, state):
        self._sessions[state.sid] = Hict(state)

    def destroy_state(self, state):
        del self._sessions[state.sid]

    def store_prelogin(self, origin, sid, **argd):
        self._prelogins[origin][sid] = Hict(argd)

    def fetch_prelogin(self, origin, domain, sid):
        prelogins = self._prelogins.get(origin, None)
        if prelogins and sid in prelogins:
            prelogin = prelogins.pop(sid)
            if prelogin.domain == domain:
                return prelogin

        return None

    def prelogin_count(self, domain, origin):
        tstamp = timestamp()
        prelogins = self._prelogins[origin]
        for k, v in prelogins.items():
            if v.expires <= tstamp:
                del prelogins[k]
        return len(prelogins)

    def abuse_level_by_origin(self, origin, domain):
        watch_period = timestamp() - hooks.abuse_level_watch_period(domain)
        return sum(l for t, l, _ in self._abuses[origin] if t >= watch_period)

    def incr_abuse(self, origin, domain, incr=1, abuse=None):
        self._abuses[origin].append((timestamp(), incr, abuse))
