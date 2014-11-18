"""
Toy storage implementation using rethinkdb.
"""

from _term import Hict, parse_term, dump_term as dumps, load_term as loads
from _auth import default_settings, hooks
from _state import get_state
from _admin import Profile
from _store import Record
from _exc import RecordVersionMismatch, DuplicatedRecordID

import _config as conf

from base64 import b64encode, b64decode
from collections import defaultdict
from time import time as timestamp
import rethinkdb as rtdb

# default models names
Profile = Profile.__name__
State = '_state_'
Txn = '_txn_'
Prelogin = '_prelogin_'
Abuse = '_abuse_'
Acl = '_acl_'
Settings = '_settings_'


class RTModel(object):
    pass


class RTStore(object):

    transactional = False

    def __init__(self, host='localhost', port=28015):
        self.conn = rtdb.connect(host=host, port=port)
        self.indexed = set()

    # -- connection & schema ---------------------------------

    def add_model(self, model, add_index):
        if add_index is True:
            self.indexed.add(model)

    def get_connection(self, domain):
        conn = self.conn
        try:
            rtdb.db_create(domain).run(conn)
            self.init_domain_store_schema(conn, domain)
        except:
            pass
        return conn

    def init_domain_store_schema(self, conn, domain):
        db = rtdb.db(domain)

        tables = set(db.table_list().run(conn))

        for table, (pk, indexes) in {
                Txn: ('txn', ['origin', 'tstamp', 'identity']),
                State: ('sid', ['origin', 'identity', 'expires']),
                Prelogin: ('sid', ['origin', 'identity', 'expires']),
                Abuse: (None, ['origin', 'tstamp']),
                Acl: (None, ['type', 'name', 'role']),
                Settings: ('key', [])}.items():

            if table not in tables:
                if pk is not None:
                    db.table_create(table, primary_key=pk).run(conn)
                else:
                    db.table_create(table).run(conn)

                for index in indexes:
                    db.table(table).index_create(index).run(conn)

                if table == Settings:
                    db.table(Settings).insert([
                        dict(key=k, value=getattr(conf, k.upper()))
                        for k in default_settings]).run(conn)

    def get_model(self, domain, model):
        # db name can only have alphanum and underscores
        domain = domain.encode('hex')

        conn = self.get_connection(domain)
        db = rtdb.db(domain)

        try:
            db.table_create(model, primary_key='uuid').run(conn)
            db.table(model).index_create('txn').run(conn)
            db.table(model).index_create('vsn').run(conn)
        except:
            pass

        return conn, db.table(model)

    def get_model_hist(self, domain, model):
        # db name can only have alphanum and underscores
        domain = domain.encode('hex')

        conn = self.get_connection(domain)
        model_hist = '%s_hist' % model
        db = rtdb.db(domain)

        try:
            db.table_create(model_hist).run(conn)
            db.table(model_hist).index_create('uuid').run(conn)
            db.table(model_hist).index_create('txn').run(conn)
            db.table(model_hist).index_create('vsn').run(conn)
        except:
            pass

        return conn, db.table(model_hist)

    # -- transaction -----------------------------------------

    def begin(self, domain, txn):
        pass

    def commit(self, domain, txn, state, log=None):
        profile = str(state.profile._uuid) if state.profile else None
        data = dumps(dict(log=log, state=state))
        conn, table = self.get_model(domain, Txn)
        table.insert(dict(txn=str(txn), origin=state.origin,
                          tstamp=timestamp(), profile=profile,
                          data=data)).run(conn)

    def rollback(self, domain, txn):
        pass

    # -- crud ------------------------------------------------

    def fetch(self, domain, model, uuid, vsn=None, txn=None):
        conn, table = self.get_model(domain, model)

        if vsn is not None:
            row = table.find_one(uuid=uuid, vsn=vsn)
        else:
            row = table.find_one(uuid=uuid)

        if row is not None:
            return (row['vsn'], row['txn'], loads(row['data']))

    def store(self, domain, txn, insert=None, update=None, delete=None):
        if insert:
            self.insert(domain, txn, insert)
        if update:
            self.update(domain, txn, update)
        if delete:
            self.delete(domain, txn, delete)

    def insert(self, domain, txn, records):
        index = bool(self.indexer is self)
        get_model_hist = self.get_model_hist
        get_model = self.get_model
        rows = defaultdict(list)
        tables = dict()

        for record in records:
            model, uuid = record._model, str(record._uuid)

            if model not in tables:
                conn, table = tables[model] = get_model_hist(domain, model)
            else:
                conn, table = tables[model]

            if table.get(uuid).run(conn) is not None:
                raise DuplicatedRecordID(domain, model, uuid)

            row = dict(vsn=record._vsn, uuid=uuid, txn=str(txn),
                       data=dumps(record._dct))

            if index is True:
                row.update(record._indexer(record))

            rows[model].append(row)

        for model, rows in rows.iteritems():
            conn, table = get_model(domain, model)
            table.insert(rows).run(conn)

    def update(self, domain, txn, records):
        index = bool(self.indexer is self)
        get_model_hist = self.get_model_hist
        get_model = self.get_model
        tables = dict()

        for record in records:
            model, uuid, vsn = record._model, str(record._uuid), record._vsn

            if model not in tables:
                conn, table = get_model(domain, model)
                _, hist = get_model_hist(domain, model)
                tables[model] = (conn, table, hist)
            else:
                conn, table, hist = tables[model]

            stored = table.find_one(uuid=uuid).run(conn)
            if stored['vsn'] != (vsn - 1):
                raise RecordVersionMismatch(domain, model, uuid, vsn)

            row = dict(vsn=vsn, uuid=uuid, txn=str(txn),
                       data=dumps(record._dct))

            if index is True:
                row.update(record._indexer(record))

            hist.insert(stored).run(conn)
            table.update(row).run(conn)

    def delete(self, domain, txn, records):
        get_model_hist = self.get_model_hist
        get_model = self.get_model
        tables = dict()

        for record in records:
            model, uuid, vsn = record._model, str(record._uuid), record._vsn

            if model not in tables:
                conn, table = get_model(domain, model)
                _, hist = get_model_hist(domain, model)
                tables[model] = (conn, table, hist)
            else:
                conn, table, hist = tables[model]

            stored = table.find_one(uuid=uuid).run(conn)
            if stored['vsn'] != -vsn:
                raise RecordVersionMismatch(domain, model, uuid, vsn)

            hist.insert(stored).run(conn)
            row = dict(uuid=uuid, vsn=vsn, txn=str(txn))
            table.update(row).run(conn)

    # -- fuzzy & relational query ------------------------------

    def search(self, domain, model, fun):
        if (self.indexer or self) is self:
            raise NotImplementedError
        else:
            yield self.indexer.search(domain, model, fun)

    def select(self, domain, model, fun):
        if (self.indexer or self) is self:
            conn, table = self.get_model(domain, model)
            table.find = lambda **qry: table.filter(qry)
            for row in fun(table).run(conn):
                yield Record(model, row.pop('uuid'), vsn=row['vsn'],
                             txn=row['txn'], **loads(row['data']))
        else:
            yield self.indexer.select(domain, model, fun)

    # -- auth hooks --------------------------------------------

    def _fetch_setting(self, domain, key, fail=None, parser=parse_term):
        conn, table = self.get_model(domain, Settings)
        for row in table.filter(dict(key=key)).limit(1).run(conn):
            if parser is not None:
                return parser(row['value'])
            else:
                return row['value']
        return fail

    def _fetch_record(self, domain, model, **terms):
        conn, table = self.get_model(domain, model)
        for row in table.filter(terms).limit(1).run(conn):
            return Record(model, row['uuid'], vsn=row['vsn'],
                          txn=row['txn'], **loads(row['data']))

    def fetch_profile(self, domain, identity, **extra):
        return self._fetch_record(domain, Profile, username=identity, **extra)

    def prelogin_count(self, domain, origin):
        conn, table = self.get_model(domain, Prelogin)
        return table.count(dict(origin=origin)).run(conn)

    def fetch_prelogin(self, origin, domain, sid):
        conn, table = self.get_model(domain, Prelogin)
        try:
            enc_sid = b64encode(sid)
            rs = table.get(enc_sid).delete(return_vals=True).run(conn)
            prelogin = Hict(rs['old_val'])
            assert b64decode(prelogin.sid) == sid
            prelogin.update(**loads(prelogin.pop('data')))
            return prelogin
        except:
            pass

    def store_prelogin(self, origin, domain, sid, identity, expires, **data):
        row = dict(origin=origin, identity=identity, expires=expires,
                   sid=b64encode(sid), data=dumps(data))
        conn, table = self.get_model(domain, Prelogin)
        table.insert(row).run(conn)

    def load_state(self, domain, sid):
        conn, table = self.get_model(domain, State)
        row = table.get(b64encode(sid)).run(conn)
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
        conn, table = self.get_model(state.domain, State)
        try:
            assert table.update(row).run(conn)['replaced'] == 1
        except:
            assert table.insert(row).run(conn)['inserted'] == 1

    def destroy_state(self, state):
        conn, table = self.get_model(state.domain, State)
        table.get(b64encode(state.sid)).delete().run(conn)

    def active_user_sessions(self, domain, identity):
        conn, table = self.get_model(domain, State)
        qry = (rtdb.row['identity'] == identity) \
            & (rtdb.row['expires'] > timestamp())
        return table.count(qry).run(conn)

    def destroy_sessions(self, domain, identity):
        conn, table = self.get_model(domain, State)
        table.filter(dict(identity=identity)).delete().run(conn)

    def incr_abuse(self, origin, domain, incr=1, abuse=None):
        data = dumps(abuse) if abuse is not None else abuse
        row = dict(origin=origin, level=incr, tstamp=timestamp(), data=data)
        conn, table = self.get_model(domain, Abuse)
        table.insert(row).run(conn)

    def abuse_level_by_origin(self, origin, domain):
        conn, table = self.get_model(domain, Abuse)
        watch_period = timestamp() - hooks.abuse_level_watch_period(domain)
        qry = (rtdb.row['origin'] == origin) \
            & (rtdb.row['tstamp'] >= watch_period)
        return sum(doc['level'] for doc in table.filter(qry).run(conn))

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
