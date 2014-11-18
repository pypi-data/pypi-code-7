"""
Toy storage implementation using ElasticSearch.

WARNING: not working and incomplete!
"""

from elasticsearch import Elasticsearch as ES, serializer
from elasticsearch.helpers import bulk

from time import time as timestamp
from _store import Record
from _auth import hooks
from _term import to_simple, UUID

'''
# monkey patch elasticsearch serializer
def dumps(term, *args, **argd):
    simple = to_simple(term)
    json = to_json(simple)
    return json

serializer.json.dumps = dumps
'''

Prelogin = 'Prelogin'
Session = 'Session'
Abuse = 'Abuse'


class ElasticSearch(object):

    def __init__(self, *args, **argd):
        self._es = ES(*args, **argd)

    def do_nothing(self, *args, **argd):
        pass
    begin = commit = rollback = add_model = do_nothing

    def _bulk_actions(self, index, txn, inserts=None, updates=None, deletes=None):  # noqa
        for (action, records, source) in (('create', inserts, True),
                                          ('update', updates, True),
                                          ('delete', deletes, False)):
            if records:
                for record in records:
                    if source:
                        source = to_simple(record._dct)
                        source.update(_txn=str(txn))
                    yield dict(_index=index,
                               _op_type=action,
                               _type=record._model,
                               _id=str(record._uuid),
                               _version=record._vsn,
                               _source=source or None)

    def store(self, domain, txn, inserts=None, updates=None, deletes=None):
        actions = self._bulk_actions(domain, txn, inserts, updates, deletes)
        bulk(self._es, actions, raise_on_error=True)

    def fetch(self, domain, model, uuid, vsn=None, txn=None):
        document = self._es.get(index=domain, doc_type=model, id=uuid, version=vsn) # noqa
        _source = document['_source']
        _version = document['_version']
        _txn = _source.pop('_txn', None)
        if _txn is not None:
            _txn = UUID(_txn)
        assert not vsn or _version == vsn, 'version-mismatch'
        assert not txn or _txn == txn, 'txn-mismatch'
        return _version, _txn, _source

    def query(self, domain, model, fun=None, score=None, source=False):
        es = self._es
        es.indices.create(index=domain, ignore=400)
        result = fun(domain, model, es)
        print result
        for document in result['hits']['hits']:
            _source = document['_source']
            _version = document['_version']
            _txn = _source.pop('_txn', None)
            if _txn is not None:
                _txn = UUID(_txn)
            _id = UUID(document['_id'])
            if source is True:
                yield (_id, _version, _txn, _source)
            elif score is not None:
                #TODO: extract real document score
                yield (_id, _version, _txn, score)
            else:
                yield (_id, _version, _txn)

    def search(self, domain, model, fun):
        return self.query(domain, model, fun, 1)

    def select(self, domain, model, fun=None):
        return self.query(domain, model, fun)

    def find(self, domain, model, terms):
        query = ' AND '.join('%s:"%s"' % i for i in terms.items())
        search = lambda _d, _m, es: es.search(index=domain, doc_type=model, q=query)  # noqa
        for uuid, vsn, txn, dct in self.query(domain, model, search):
            return Record(model, uuid, vsn, txn, dct)

    def fetch_profile(self, domain, identity, **extra):
        extra.update(username=identity)
        return self.find(domain, 'Profile', extra)

    def has_permission(self, state, call):
        return True

    def active_user_sessions(self, domain, identity):
        query = 'identity:"%s" AND expires:[%s TO *]' % (identity, timestamp())
        return self._es.count(index=domain, doc_type=Session, q=query)

    def destroy_sessions(self, domain, identity):
        body = {'term': {'identity': identity}}
        self._es.delete_by_query(index=domain, doc_type=Session, body=body)

    def load_state(self, domain, sid):
        return self._es.get(index=domain, doc_type=Session, id=sid, source=True)    # noqa

    def store_state(self, state):
        self._es.index(index=state.domain, doc_type=Session,
                       id=state.sid, body=state)

    def destroy_state(self, state):
        self._es.delete(index=state.domain, doc_type=Session, id=state.sid)

    def store_prelogin(self, domain, sid, **argd):
        self._es.create(index=domain, doc_type=Prelogin, id=sid,
                        body=to_simple(argd), raise_on_error=True)

    def fetch_prelogin(self, origin, domain, sid):
        es = self._es
        if es.exists(index=domain, doc_type=Prelogin, id=sid):
            prelogin = es.get(index=domain, doc_type=Prelogin, id=sid, source=True) # noqa
            es.delete(index=domain, doc_type=Prelogin, id=sid)
            return prelogin if prelogin['origin'] == origin else None

    def prelogin_count(self, domain, origin):
        query = 'origin:"%s" AND expires:[%s TO *]' % (origin, timestamp())
        return self._es.count(index=domain, doc_type=Prelogin, q=query)

    def abuse_level_by_origin(self, origin, domain):
        watch_period = timestamp() - hooks.abuse_level_watch_period(domain)
        query = 'origin:"%s" AND expires:[%s TO *]' % (origin, watch_period)
        docs = self._es.search(index=domain, doc_type=Abuse, q=query, source=True)  # noqa
        return sum(d['incr'] for d in docs)

    def incr_abuse(self, origin, domain, incr=1, abuse=None):
        body = dict(origin=origin, incr=incr, abuse=abuse, expires=timestamp())
        self._es.index(index=domain, doc_type=Abuse, body=body)
