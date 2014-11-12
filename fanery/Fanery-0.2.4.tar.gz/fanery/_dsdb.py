"""
Toy storage implementation using dataset.
"""

from _term import Hict, parse_term, dump_term as dumps, load_term as loads
from _auth import default_settings, hooks, Profile
from _state import get_state
from _store import Record
from _exc import RecordVersionMismatch, DuplicatedRecordID

import _config as conf

from sqlalchemy import LargeBinary, String, Integer, Float as Timestamp
from base64 import b64encode, b64decode
from collections import defaultdict
from time import time as timestamp
from dataset import connect
from os.path import join

# default storage url
MEMORY_DB_URL = 'sqlite:///:memory:'

# default models names
Profile = Profile.__name__
State = '_state_'
Txn = '_txn_'
Prelogin = '_prelogin_'
Abuse = '_abuse_'
Acl = '_acl_'
Settings = '_settings_'


class DSStore(object):

    def __init__(self, uri_prefix=None, **argd):
        self.uri_prefix = uri_prefix
        self.conn_argd = argd
        self.conns = dict()
        self.indexed = set()

    # -- connection & schema ---------------------------------

    def add_model(self, model, add_index):
        if add_index is True:
            self.indexed.add(model)

    def get_connection(self, domain):
        try:
            return self.conns[domain]
        except KeyError:
            if self.uri_prefix is None:
                url = MEMORY_DB_URL
            else:
                url = join(self.uri_prefix, domain)
            conn = connect(url, **self.conn_argd)
            self.init_domain_store_schema(conn)
            return self.conns.setdefault(domain, conn)

    def init_domain_store_schema(self, conn):
        try:
            conn.load_table(Settings)
        except:
            table = conn.create_table(Txn, 'txn', 'String')
            table.create_column('origin', String)
            table.create_column('identity', String)
            table.create_column('tstamp', Timestamp)
            table.create_column('data', LargeBinary)
            table.create_index(['origin', 'tstamp', 'identity'])

            table = conn.create_table(State, 'sid', 'String')
            table.create_column('origin', String)
            table.create_column('identity', String)
            table.create_column('expires', Timestamp)
            table.create_column('data', LargeBinary)
            table.create_index(['origin', 'identity', 'expires'])

            table = conn.create_table(Prelogin, 'sid', 'String')
            table.create_column('origin', String)
            table.create_column('identity', String)
            table.create_column('expires', Timestamp)
            table.create_column('data', LargeBinary)
            table.create_index(['origin', 'identity', 'expires'])

            table = conn.create_table(Abuse)
            table.create_column('origin', String)
            table.create_column('level', String)
            table.create_column('tstamp', Timestamp)
            table.create_column('data', LargeBinary)
            table.create_index(['origin', 'tstamp'])

            table = conn.create_table(Acl)
            table.create_column('type', Integer)
            table.create_column('name', String)
            table.create_column('role', String)
            table.create_column('perm', Integer)
            table.create_index(['type', 'name', 'role'])

            table = conn.create_table(Settings, 'key', 'String')
            table.create_column('value', String)
            table.insert_many([dict(key=k, value=getattr(conf, k.upper()))
                               for k in default_settings], ensure=False)

    def get_model(self, domain, model):
        conn = self.get_connection(domain)
        try:
            table = conn.load_table(model)
        except:
            table = conn.create_table(model, 'uuid', 'String')
            table.create_column('txn', String)
            table.create_column('vsn', Integer)
            table.create_column('data', LargeBinary)
            table.create_index(['txn', 'vsn'])
        else:
            if model in self.indexed:
                missing = [name for name, column
                           in table.table.columns.items()
                           if not column.index and name != 'data']
                if missing:
                    table.create_index(missing)

        return table

    def get_model_hist(self, domain, model):
        conn = self.get_connection(domain)
        model_hist = '%s_hist' % model
        try:
            table = conn.load_table(model_hist)
        except:
            table = conn.create_table(model_hist)
            table.create_column('uuid', String)
            table.create_column('txn', String)
            table.create_column('vsn', Integer)
            table.create_column('data', LargeBinary)
            table.create_index(['uuid', 'txn', 'vsn'])

        return table

    # -- transaction -----------------------------------------

    def begin(self, domain, txn):
        self.get_connection(domain).begin()

    def commit(self, domain, txn, state, log=None):
        self.get_model(domain, '_txn_').insert(dict(
            txn=str(txn), origin=state.origin, tstamp=timestamp(),
            profile=str(state.profile._uuid) if state.profile else None,
            data=dumps(dict(log=log, state=state or get_state()))))
        self.get_connection(domain).commit()

    def rollback(self, domain, txn):
        self.get_connection(domain).rollback()

    # -- crud ------------------------------------------------

    def fetch(self, domain, model, uuid, vsn=None, txn=None):
        table = self.get_model(domain, model)

        if vsn is not None:
            row = table.find_one(uuid=str(uuid), vsn=vsn)
        else:
            row = table.find_one(uuid=str(uuid))

        if row is not None:
            return (row['vsn'], row['txn'], loads(row['data']))

    def store(self, domain, txn, inserts=None, updates=None, deletes=None):
        if inserts:
            self.insert(domain, txn, inserts)
        if updates:
            self.update(domain, txn, updates)
        if deletes:
            self.delete(domain, txn, deletes)

    def insert(self, domain, txn, records):
        get_model_hist = self.get_model_hist
        get_model = self.get_model
        rows = defaultdict(list)
        indexed = self.indexed

        for record in records:
            model, uuid = record._model, str(record._uuid)

            if get_model_hist(domain, model).find_one(uuid=uuid):
                raise DuplicatedRecordID(domain, model, uuid)

            row = dict(vsn=record._vsn, uuid=uuid, txn=str(txn),
                       data=dumps(record._dct))

            if model in indexed:
                row.update(record._indexer(record))

            rows[model].append(row)

        for model, rows in rows.iteritems():
            get_model(domain, model).insert_many(rows)

    def update(self, domain, txn, records):
        get_model_hist = self.get_model_hist
        get_model = self.get_model
        indexed = self.indexed

        for record in records:
            model, uuid, vsn = record._model, str(record._uuid), record._vsn
            table = get_model(domain, model)

            stored = table.find_one(uuid=uuid)
            if stored['vsn'] != (vsn - 1):
                raise RecordVersionMismatch(domain, model, uuid, vsn)

            row = dict(vsn=vsn, uuid=uuid, txn=str(txn),
                       data=dumps(record._dct))

            if model in indexed:
                row.update(record._indexer(record))

            get_model_hist(domain, model).insert(stored)
            table.update(row)

    def delete(self, domain, txn, records):
        get_model_hist = self.get_model_hist
        get_model = self.get_model

        for record in records:
            model, uuid, vsn = record._model, str(record._uuid), record._vsn
            table = get_model(domain, model)

            stored = table.find_one(uuid=uuid)
            if stored['vsn'] != -vsn:
                raise RecordVersionMismatch(domain, model, uuid, vsn)

            get_model_hist(domain, model).insert(stored)
            row = dict((c, None) for c in table.columns)
            row.update(uuid=uuid, vsn=vsn, txn=str(txn))
            table.update(row)

    # -- fuzzy & relational query ------------------------------

    def search(self, domain, model, fun):
        raise NotImplementedError

    def select(self, domain, model, fun=None):
        if fun is None:
            fun = lambda tbl: tbl.database.query("SELECT * FROM %s" % model)
        for row in fun(self.get_model(domain, model)):
            yield Record(model, row.pop('uuid'), vsn=row['vsn'],
                         txn=row['txn'], **loads(row['data']))

    def find(self, domain, model, terms):
        return self.get_model(domain, model).find_one(**terms)

    # -- auth hooks --------------------------------------------

    def _fetch_setting(self, domain, key, fail=None, parser=parse_term):
        table = self.get_model(domain, Settings)
        try:
            row = table.find_one(key=key)
            if parser is not None:
                return parser(row['value'])
            else:
                return row['value']
        except:
            return fail

    def _fetch_record(self, domain, model, **terms):
        row = self.get_model(domain, model).find_one(**terms)
        if row is not None:
            return Record(model, row.pop('uuid'), vsn=row['vsn'],
                          txn=row['txn'], **loads(row['data']))

    def fetch_profile(self, domain, identity, **extra):
        return self._fetch_record(domain, Profile, username=identity, **extra)

    def prelogin_count(self, domain, origin):
        db = self.get_model(domain, Prelogin).database
        sql = '''DELETE FROM %s WHERE origin = :origin
                                  AND expires <= :tstamp'''
        db.query(sql % Prelogin, origin=origin, tstamp=timestamp())
        sql = '''SELECT COUNT(*) AS active FROM %s
                  WHERE origin = :origin'''
        row = db.query(sql % Prelogin, origin=origin).next()
        return row['active']

    def fetch_prelogin(self, origin, domain, sid):
        table = self.get_model(domain, Prelogin)
        db = table.database
        db.begin()
        try:
            enc_sid = b64encode(sid)
            row = table.find_one(sid=enc_sid, origin=origin)
            if row is not None:
                assert sid == b64decode(row.pop('sid'))
                prelogin = Hict(sid=sid, **row)
                prelogin.update(**loads(prelogin.pop('data')))
                return prelogin
        finally:
            table.delete(sid=enc_sid, origin=origin)
            db.commit()

    def store_prelogin(self, origin, domain, sid, identity, expires, **data):
        row = dict(origin=origin, identity=identity, expires=expires,
                   sid=b64encode(sid), data=dumps(data))
        self.get_model(domain, Prelogin).insert(row)

    def load_state(self, domain, sid):
        row = self.get_model(domain, State).find_one(sid=b64encode(sid))
        if row:
            assert sid == b64decode(row.pop('sid'))
            profile = self._fetch_record(domain, Profile, uuid=row.pop('profile'))  # noqa
            state = Hict(sid=sid, **loads(row.pop('data'), dict_type=Hict))
            state.update(profile=profile, **row)
            return state

    def store_state(self, state):
        profile = state.profile
        data = dict(skey=state.skey, ckey=state.ckey, sseed=state.sseed,
                    vkey=state.vkey, pads=state.pads, data=state.data,
                    role=state.role, impersonated_by=state.impersonated_by)
        row = dict(sid=b64encode(state.sid), identity=profile.username,
                   profile=str(profile._uuid), origin=state.origin,
                   expires=state.expires, data=dumps(data))
        self.get_model(state.domain, State).upsert(row, keys=('sid',))

    def destroy_state(self, state):
        self.get_model(state.domain, State).delete(sid=b64encode(state.sid))

    def active_user_sessions(self, domain, identity):
        db = self.get_model(domain, State).database
        sql = '''SELECT COUNT(*) AS active FROM %s
                  WHERE identity = :identity
                    AND expires > :expires'''
        params = dict(identity=identity, expires=timestamp())
        row = db.query(sql % State, **params).next()
        return row['active']

    def destroy_sessions(self, domain, identity):
        self.get_model(domain, State).delete(identity=identity)

    def incr_abuse(self, origin, domain, incr=1, abuse=None):
        data = dumps(abuse) if abuse is not None else abuse
        row = dict(origin=origin, level=incr, tstamp=timestamp(), data=data)
        self.get_model(domain, Abuse).insert(row)

    def abuse_level_by_origin(self, origin, domain):
        watch_period = timestamp() - hooks.abuse_level_watch_period(domain)
        db = self.get_model(domain, Abuse).database
        sql = '''SELECT SUM(level) AS abuse_level FROM %s
                  WHERE origin = :origin
                    AND tstamp >= :watch_period'''
        params = dict(origin=origin, watch_period=watch_period)
        row = db.query(sql % Abuse, **params).next()
        return row['abuse_level'] or 0

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
