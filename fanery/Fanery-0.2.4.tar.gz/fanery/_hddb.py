"""
Toy storage implementation using HyperDex.
"""

from _term import (
    Hict, parse_term, is_number,
    dump_term as dumps, load_term as loads
)
from _auth import default_settings, hooks
from _random import rand_uuid
from _state import get_state
from _admin import Profile
from _store import Record
from _exc import RecordVersionMismatch, DuplicatedRecordID

import _config as conf

from time import time as timestamp
from bsdiff4 import diff as bsdiff
from hyperdex.admin import Admin
from hyperdex.client import Client

# default models names
Profile = Profile.__name__
State = '_state_'
Txn = '_txn_'
Prelogin = '_prelogin_'
Abuse = '_abuse_'
Acl = '_acl_'
Settings = '_settings_'

# schema templates
spaces = Hict(index='''
              space _idx_%s
              key id
              attributes
                string domain,
                string uuid,
                int vsn,
                string field,
                int num,
                float dec,
                string str
              subspace domain, uuid
              subspace domain, field, num
              subspace domain, field, dec
              subspace domain, field, str
              ''',
              model='''
              space %s
              key uuid
              attributes
                string domain,
                int vsn,
                string txn,
                string data
              subspace domain, txn
              ''',
              hist='''
              space %s_hist
              key id
              attributes
                string domain,
                string uuid,
                int vsn,
                string txn,
                string data
              subspace domain, uuid, vsn
              subspace domain, txn
              ''',
              base=('''
                    space %s
                    key txn
                    attributes
                        string domain,
                        string origin,
                        string profile,
                        float tstamp,
                        string data
                    subspace domain, profile
                    subspace domain, tstamp
                        ''' % Txn, '''
                    space %s
                    key sid
                    attributes
                        string domain,
                        string origin,
                        string identity,
                        string profile,
                        float expires,
                        string data
                    subspace domain, origin, expires
                    subspace domain, identity
                        ''' % State, '''
                    space %s
                    key sid
                    attributes
                        string domain,
                        string origin,
                        string identity,
                        float expires,
                        string data
                    subspace domain, origin, expires
                    subspace domain, identity, expires
                        ''' % Prelogin, '''
                    space %s
                    key id
                    attributes
                        string origin,
                        float tstamp,
                        int level,
                        string data
                    subspace origin, tstamp
                        ''' % Abuse, '''
                    space %s
                    key domain
                    attributes
                        map(string,string) settings
                        ''' % Settings))


class HDStore(object):

    def __init__(self, host='localhost', port=1982):
        self.adm = adm = Admin(host, port)
        self.cli = Client(host, port)
        self.indexed = set()

        # initialize fanery base spaces
        for space in spaces.base:
            try:
                adm.add_space(space)
            except:
                # do nothing, exists already
                pass

    # -- model spaces ----------------------------------------

    def add_model(self, model, add_index=False):
        model_spaces = [spaces.model, spaces.hist]
        if add_index:
            model_spaces.append(spaces.index)
            self.indexed.add(model)

        adm = self.adm
        for space in model_spaces:
            try:
                adm.add_space(space % model)
            except:
                pass

    # -- transaction -----------------------------------------

    def begin(self, domain, txn):
        pass

    def commit(self, domain, txn, state, log=None):
        profile = str(state.profile._uuid) if state.profile else None
        data = dumps(dict(log=log, state=state or get_state()))
        self.cli.put(Txn, str(txn), dict(domain=domain, origin=state.origin,
                                         tstamp=timestamp(), profile=profile,
                                         data=data))

    def rollback(self, domain, txn):
        pass

    # -- crud ------------------------------------------------

    def fetch(self, domain, model, uuid, vsn=None, txn=None):
        qry = dict(domain=domain, uuid=uuid)
        if vsn is not None:
            qry['vsn'] = vsn
        if txn is not None:
            qry['txn'] = txn

        for row in self.cli.search(model, qry):
            return (row['vsn'], row['txn'], loads(row['data']))

    def store(self, domain, txn, inserts=None, updates=None, deletes=None):
        if inserts:
            self.insert(domain, txn, inserts)
        if updates:
            self.update(domain, txn, updates)
        if deletes:
            self.delete(domain, txn, deletes)

    #TODO: use async insert/update/delete?

    def insert(self, domain, txn, records):
        indexed = self.indexed
        inserts = set()
        cli = self.cli

        for record in records:
            model, uuid = record._model, str(record._uuid)

            data = dict(domain=domain, vsn=record._vsn,
                        txn=str(txn), data=dumps(record._dct))

            if not cli.put_if_not_exist(model, uuid, data):
                raise DuplicatedRecordID(domain, model, uuid)
            elif model in indexed:
                inserts.add(record)

        if inserts:
            self.index(domain, txn, inserts=inserts)

    def update(self, domain, txn, records):
        indexed = self.indexed
        updates = set()
        cli = self.cli

        for record in records:
            model, uuid, vsn = record._model, str(record._uuid), record._vsn
            stored = cli.get(model, uuid)
            data = dumps(record._dct)
            old_vsn = stored['vsn']

            if not ((old_vsn == vsn - 1) and
                    cli.cond_put(model, uuid, dict(vsn=vsn - 1),
                                 dict(domain=domain, vsn=vsn, txn=str(txn),
                                      data=data))):
                raise RecordVersionMismatch(domain, model, uuid, vsn)
            else:
                # compute reverse binary diff
                stored['data'] = bsdiff(data, stored['data'])
                cli.put('%s_hist' % model, '%s:%s' % (uuid, old_vsn), stored)

                if model in indexed:
                    updates.add(record)

        if updates:
            self.index(domain, txn, updates=updates)

    def delete(self, domain, txn, records):
        indexed = self.indexed
        deletes = set()
        cli = self.cli

        for record in records:
            model, uuid, vsn = record._model, str(record._uuid), record._vsn
            stored = cli.get(model, uuid)

            if not ((stored['vsn'] == -vsn) and
                    cli.cond_put(model, uuid, dict(vsn=-vsn),
                                 dict(domain=domain, vsn=vsn, txn=str(txn)))):
                raise RecordVersionMismatch(domain, model, uuid, vsn)
            else:
                cli.put('%s_hist' % model, '%s:%s' % (uuid, -vsn), stored)

                if model in indexed:
                    deletes.add(record)

        if deletes:
            self.index(domain, txn, deletes=deletes)

    def index(self, domain, txn, inserts=None, updates=None, deletes=None):
        purge_record_index = self.cli.delete
        store_index = self.cli.put_if_not_exist

        for put, records in ((True, inserts), (True, updates), (False, deletes)):   # noqa
            if not records:
                continue

            for record in records:
                model, uuid = '_idx_%s' % record._model, str(record._uuid)

                purge_record_index(model, dict(domain=domain, uuid=uuid))

                if put:
                    #FIXME: handle date/datetime terms
                    for field, term in record._indexer(record).items():
                        data = dict(domain=domain, uuid=uuid, vsn=record._vsn)
                        if isinstance(term, (int, long)):
                            data.update(field=field, num=term)
                        elif is_number(term):
                            data.update(field=field, dec=term)
                        elif isinstance(term, basestring):
                            data.update(field=field, str=term)
                        else:
                            continue
                        while not store_index(model, str(rand_uuid()), data):
                            continue

    # -- fuzzy, relational and by-terms query --------------------

    def search(self, domain, model, fun):
        raise NotImplementedError

    def select(self, domain, model, fun):
        yield fun(self.cli, domain, model)

    def find(self, domain, model, terms):
        model = '_idx_%s' % model

        qry = dict(domain=domain)
        #FIXME: handle date/datetime terms
        #FIXME: handle range criteria
        for k, v in terms.items():
            if isinstance(v, (int, long)):
                qry.update(field=k, num=v)
            elif is_number(v):
                qry.update(field=k, dec=v)
            elif isinstance(v, basestring):
                qry.update(field=k, str=str(v))

        for dct in self.cli.search(model, qry):
            if dct['domain'] == domain:
                yield dct['uuid'], dct['vsn']

    # -- auth hooks --------------------------------------------

    def _fetch_setting(self, domain, key, fail=None, parser=parse_term):
        try:
            settings = self.cli.get(Settings, domain)['settings']
        except:
            settings = dict((k, str(getattr(conf, k.upper())))
                            for k in default_settings)
            assert self.cli.put(Settings, domain, dict(settings=settings))
        if key not in settings:
            return fail
        elif parser is not None:
            return parser(settings[key])
        else:
            return settings[key]

    def _fetch_record(self, domain, model, uuid=None, **terms):
        if uuid:
            stored = self.cli.get(model, str(uuid))
            vsn = stored['vsn']
        elif terms:
            for uuid, vsn in self.find(domain, model, terms):
                stored = self.cli.get(model, uuid)
                if stored['vsn'] == vsn:
                    break

        if stored['domain'] == domain:
            return Record(model, uuid=uuid, vsn=vsn, txn=stored['txn'],
                          **loads(stored['data']))

    def fetch_profile(self, domain, identity, **extra):
        return self._fetch_record(domain, Profile, username=identity, **extra)

    def prelogin_count(self, domain, origin):
        return self.cli.count(Prelogin, dict(domain=domain, origin=origin))

    def fetch_prelogin(self, origin, domain, sid):
        cli = self.cli
        try:
            prelogin = Hict(cli.get(Prelogin, sid))
            if prelogin.domain == domain and prelogin.origin == origin:
                cli.delete(Prelogin, sid)
                prelogin.update(**loads(prelogin.pop('data')))
                return prelogin
        except:
            pass

    def store_prelogin(self, origin, domain, sid, identity, expires, **data):
        self.cli.put(Prelogin, sid, dict(origin=origin, domain=domain,
                                         identity=str(identity),
                                         expires=expires,
                                         data=dumps(data)))

    def load_state(self, domain, sid):
        try:
            stored = self.cli.get(State, sid)
            if stored['domain'] == domain:
                profile = self._fetch_record(domain, Profile, stored.pop('profile'))  # noqa
                state = loads(stored.pop('data'), dict_type=Hict)
                state.update(sid=sid, profile=profile, **stored)
                return state
        except:
            pass

    def store_state(self, state):
        profile = state.profile
        data = dict(skey=state.skey, ckey=state.ckey, sseed=state.sseed,
                    vkey=state.vkey, pads=state.pads, data=state.data,
                    role=state.role, impersonated_by=state.impersonated_by)
        assert self.cli.put(State, state.sid,
                            dict(identity=str(profile.username),
                                 profile=str(profile._uuid),
                                 domain=state.domain,
                                 origin=state.origin,
                                 data=dumps(data),
                                 expires=state.expires))

    def destroy_state(self, state):
        self.cli.delete(State, state.sid)

    def active_user_sessions(self, domain, identity):
        return self.cli.count(State, dict(domain=domain, identity=identity,
                                          expires=(timestamp(), 2 ** 31)))

    def destroy_user_sessions(self, domain, identity):
        self.cli.group_del(State, dict(domain=domain, identity=identity))

    def incr_abuse(self, origin, domain, incr=1, abuse=None):
        self.cli.put(Abuse, str(rand_uuid()),
                     dict(origin=origin, level=incr, tstamp=timestamp(),
                          data=dumps(abuse) if abuse is not None else abuse))

    def abuse_level_by_origin(self, origin, domain):
        watch_period = timestamp() - hooks.abuse_level_watch_period(domain)
        query = dict(origin=origin, tstamp=(watch_period, float(2 ** 31)))
        return sum(doc['level'] for doc in self.cli.search(Abuse, query))

    def reset_origin_abuse_level(self, origin, domain):
        self.cli.group_del(Abuse, dict(origin=origin))

    def session_timeout(self, domain):
        return self._fetch_setting(domain, 'session_timeout')

    def max_prelogin_count(self, domain):
        return self._fetch_setting(domain, 'max_prelogin_count')

    def abuse_level_watch_period(self, domain):
        return self._fetch_setting(domain, 'abuse_level_watch_period')

    def max_origin_abuse_level(self, domain):
        return self._fetch_setting(domain, 'max_origin_abuse_level')

    def max_active_user_sessions(self, domain, identity):
        return self._fetch_setting(domain, 'max_active_user_sessions')

    def has_permission(self, state, call):
        return True
