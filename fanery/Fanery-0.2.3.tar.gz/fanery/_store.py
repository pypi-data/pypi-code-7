"""
Storage proxy machinery. Not an ORM.
"""
__all__ = ['add_storage', 'add_model', 'Record', 'DataStore', 'storage']

from collections import defaultdict
from _term import parse_term, gen_uuid, is_class
from _auth import hooks, default_settings
from _state import get_state
import _exc as exc

from time import time as timestamp

import logging
logger = logging.getLogger('fanery.storage')

storage_reg = dict()
model_reg = dict()


class DataStore():

    def __init__(self, storage, fuzzy=None, relational=None, permission=None,
                 state=None, abuse=None, profile=None, settings=None):
        """
        When building the storage strategy for your models keep in mind:

        1. It should support multitenancy.
        2. Indexing and persistency should be handled by separate and
           specialized database engines.
        3. Each model/data-type may be handled by a different database engine.
        4. Use real high-available elastic database and search engines with
           predictable low latency.
        5. Avoid engines that only offer eventual consistency.
        6. Avoid propietary/closed-source Software solutions.
        """
        relay = self.__dict__

        # attach data persistence behaviours

        relay.update(store=storage.store,
                     fetch=storage.fetch,
                     begin=storage.begin,
                     commit=storage.commit,
                     rollback=storage.rollback)

        # attach data indexing behaviours

        indexers = set()

        if fuzzy is None:
            fuzzy = storage
        elif fuzzy is not storage:
            indexers.add(fuzzy)

        if relational is None:
            relational = storage
        elif relational is not storage:
            indexers.add(relational)

        indexers = tuple(indexers)

        relay.update(search=fuzzy.search,
                     find=relational.find,
                     select=relational.select,
                     indexers=indexers)

        # attach schema creation delegator

        add_index = bool(relational is storage or fuzzy is storage)

        def add_model(model):
            storage.add_model(model, add_index=add_index)
            for indexer in indexers:
                indexer.add_model(model)

        relay.update(add_model=add_model)

        # register auth hooks

        if permission is not None:
            hooks.has_permission = permission.has_permission

        if settings is not None:
            hooks.update((name, getattr(settings, name))
                         for name in default_settings
                         if hasattr(settings, name))

        if profile is not None:
            hooks.fetch_profile = profile.fetch_profile

        if abuse is not None:
            hooks.update(incr_abuse=abuse.incr_abuse,
                         abuse_level_by_origin=abuse.abuse_level_by_origin)

        if state is not None:
            hooks.update(load_state=state.load_state,
                         store_state=state.store_state,
                         destroy_state=state.destroy_state,
                         active_user_sessions=state.active_user_sessions,
                         destroy_user_sessions=state.destroy_sessions,
                         fetch_prelogin=state.fetch_prelogin,
                         store_prelogin=state.store_prelogin,
                         prelogin_count=state.prelogin_count)


def add_storage(storage, *models):
    for model in (models or model_reg.keys()):
        model = getattr(model, '__name__', model)
        assert model in model_reg, ('unknown-model', model)
        storage_reg[model] = storage
        storage.add_model(model)


def add_model(model, validator=None, initializer=None, indexer=None):
    name = getattr(model, '__name__', model)
    model_reg[name] = (getattr(model, 'validate', validator),
                       getattr(model, 'initialize', initializer),
                       getattr(model, 'index', indexer))


def get_storage(model):
    if model not in storage_reg:
        raise exc.UnknownModel(model)
    return storage_reg[model]


def get_validator(model):
    return model_reg[model][0] if model in model_reg else None


def get_initializer(model):
    return model_reg[model][1] if model in model_reg else None


def get_indexer(model):
    return model_reg[model][2] if model in model_reg else None


def get_fields(model):
    return model_reg[model][3] if model in model_reg else None


class Aict(dict):
    """
    Hierarchical dotted dictionary with value auto-parsing.
    """

    def __missing__(self, key):
        term = self[key] = Aict()
        return term

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, parse_term(value, dict_type=Aict))

    __setattr__ = __setitem__
    __getattr__ = dict.__getitem__
    __delattr__ = dict.__delitem__


# record marks
UNDEF, INSERT, UPDATE, DELETE = range(4)


class Record(object):

    def __init__(self, model, uuid, vsn, txn=None, _dct_=None, **dct):
        model = getattr(model, '__name__', model)
        self._store = store = get_storage(model)
        if _dct_:
            self._dct = parse_term(_dct_, dict_type=Aict)
        elif dct:
            self._dct = parse_term(dct, dict_type=Aict)
        elif vsn > 0:
            record_data = store.get(uuid, txn, vsn, txn)
            if not record_data:
                raise exc.RecordNotFound(model, uuid, vsn)
            txn, data = record_data
            self._dct = parse_term(data, dict_type=Aict)
        self._mark = UNDEF
        self._model = model
        self._uuid = parse_term(uuid)
        self._vsn = parse_term(vsn)
        self._txn = parse_term(txn)
        self._indexer = get_indexer(model)
        initialize = get_initializer(model)
        if initialize:
            initialize(self)

    def __str__(self):
        return '<Record "%s" %s:%d>' % (self._model, self._uuid, self._vsn)
    __repr__ = __str__

    def __getattr__(self, key):
        return self._dct[key]

    def __setattr__(self, key, value):
        dct = self.__dict__ if key[0] == '_' else self._dct
        dct[key] = parse_term(value, dict_type=Aict)

    def __delattr__(self, key):
        if key[0] != '_':
            del self._dct[key]

    def update(self, *args, **argd):
        self._dct.update(*args if args else argd)
        return self

    def merge(self, *args, **argd):
        dct, items = self._dct, args or argd.iteritems()
        dct.update((k, v) for k, v in items if k not in dct)
        return self


class storage(object):
    """
    The idea here is to handle all storage activities as single
    transactional unit of works inside a with statement.

        with storage("some description") as db:
            do something with db
    """

    def __init__(self, log_message=None):
        self._start = timestamp()
        self._state = state = get_state()
        self._domain = state.domain
        self._log = log_message
        self._txn = gen_uuid()
        self._cache = dict()
        self._dirty = defaultdict(set)

        logger.debug('%s %s' % (self._txn, state.service or 'init'))

    def __enter__(self):
        logger.debug("%s enter %s" % (self._txn, self._log or ''))

        return self

    def __exit__(self, type, value, traceback):
        try:
            if self._cache:
                if isinstance(value, Exception):
                    self.__rollback()
                else:
                    self.__commit()
        finally:
            logger.debug("%s %0.6f exit" % (self._txn, timestamp() - self._start))    # noqa

    def __commit(self):
        domain = self._domain
        txn = self._txn

        dirty = self._dirty
        dbms = dirty.keys()

        _start = timestamp()
        try:
            for dbm in dbms:
                dbm.begin(domain, txn)
        finally:
            logger.debug("%s %0.6f begin" % (txn, timestamp() - _start))

        try:
            for dbm, records in dirty.iteritems():
                inserts = set()
                updates = set()
                deletes = set()

                for record in records:
                    mark = record._mark
                    _vsn, _txn = record._vsn, record._txn
                    if mark is INSERT:
                        record._vsn = 1
                        inserts.add(record)
                    elif mark is UPDATE:
                        record._vsn += 1
                        updates.add(record)
                    elif mark is DELETE:
                        record._vsn *= -1
                        deletes.add(record)
                    record._mark = UNDEF
                    record._txn = txn

                _start = timestamp()
                try:
                    dbm.store(domain, txn,
                              inserts=inserts,
                              updates=updates,
                              deletes=deletes)
                finally:
                    logger.debug("%s %0.6f store ins=%d upd=%d del=%d" % (
                        txn, timestamp() - _start, len(inserts), len(updates), len(deletes)))    # noqa

                _start = timestamp()
                try:
                    for indexer in dbm.indexers:
                        indexer.index(domain, txn,
                                      inserts=inserts,
                                      updates=updates,
                                      deletes=deletes)
                finally:
                    logger.debug("%s %0.6f index" % (txn, timestamp() - _start))  # noqa

        except Exception:
            self.__rollback()
            raise

        else:
            _start = timestamp()
            try:
                for dbm in dbms:
                    dbm.commit(domain, txn, self._state, self._log)
            finally:
                logger.debug("%s %0.6f commit" % (txn, timestamp() - _start))

    def __rollback(self):
        _start = timestamp()
        try:
            for dbm in self._dirty.keys():
                dbm.rollback(self._domain, self._txn)
        finally:
            logger.debug("%s rollback [%0.6f]" % (self._txn, timestamp() - _start)) # noqa

    def fetch(self, model, uuid, vsn=None, txn=None, acl=None, fail=None):
        logger.debug("%s fetch %s %s" % (self._txn, model, uuid))

        model = getattr(model, '__name__', model)
        domain = self._domain
        cache = self._cache

        record = cache.get((model, uuid, vsn), None)
        if record and record._mark is DELETE:
            record = None
        elif record is None:
            storage = get_storage(model)
            record = storage.fetch(domain, model, uuid, vsn, txn)
            if record and not isinstance(record, Record):
                record = Record(model, uuid, *record)

        if acl and record and acl(record) is not True:
            record = None

        if record is not None:
            return cache.setdefault((model, uuid, record._vsn), record)
        elif issubclass(fail, Exception):
            raise fail
        elif callable(fail):
            return fail()
        else:
            return fail

    def query(self, method, model, fun=None, acl=None, raw=False, load=parse_term): # noqa
        _start = timestamp()
        try:
            model = getattr(model, '__name__', model)
            index = get_storage(model)
            domain = self._domain
            cache = self._cache

            for term in getattr(index, method)(domain, model, fun):
                if raw is True:
                    yield load(term) if load else term

                if isinstance(term, Record):
                    uuid, vsn, score = term._uuid, term._vsn, None
                    record = cache.setdefault((domain, model, uuid, vsn), term)
                else:
                    size = len(term)
                    if size == 4:
                        uuid, vsn, txn, score = term
                    elif size == 3:
                        uuid, vsn, txn = term
                        score = None
                    else:
                        uuid, vsn = term
                        txn = score = None
                    record = cache.get((domain, model, uuid, vsn), None)

                if record is None:
                    record = self.fetch(model, uuid, vsn, txn, acl)
                    if record is None:
                        continue
                    cache[(domain, model, uuid, vsn)] = record
                elif record._mark is DELETE or (acl and acl(record) is not True):   # noqa
                    continue
                yield (score, record) if score is not None else record
        finally:
            logger.debug("%s %0.6f %s %s %s" % (self._txn, timestamp() - _start, method, model, fun))   # noqa

    def search(self, model, fun, acl=None):
        """Fuzzy search."""
        return self.query('search', model, fun, acl)

    def select(self, model, fun=None, acl=None):
        """Relational query."""
        return self.query('select', model, fun, acl)

    def select_one(self, model, fun, acl=None, fail=None):
        for idx, record in enumerate(self.select(model, fun, acl)):
            if idx > 0:
                raise exc.MultipleRecordsFound(model)

        try:
            return record
        except:
            if is_class(fail) and issubclass(fail, Exception):
                raise fail
            elif callable(fail):
                return fail()
            else:
                return fail

    def insert(self, model, *args, **argd):
        _start = timestamp()
        try:
            model = getattr(model, '__name__', model)
            uuid, vsn = gen_uuid(), 0

            record = Record(model, uuid, vsn, self._txn, *args, **argd)
            self.validate(record)
            record._mark = INSERT
            self._dirty[record._store].add(record)
            return self._cache.setdefault((model, uuid, vsn), record)
        finally:
            logger.debug("%s %0.6f insert %s" % (self._txn, timestamp() - _start, model))   # noqa

    def update(self, *args, **argd):
        _start = timestamp()
        try:
            records = [self.fetch(*args).update(argd)] if argd else args
            for record in records:
                self.validate(record)
                mark = record._mark
                if mark is DELETE:
                    raise exc.RecordMarkedForDeletion(record)
                elif record._vsn < 0:
                    raise exc.DeletedRecord(record)
                elif mark is INSERT:
                    pass
                else:
                    record._mark = UPDATE
                    self._dirty[record._store].add(record)
        finally:
            logger.debug("%s %0.6f update %d" % (self._txn, timestamp() - _start, len(records)))    # noqa

    def delete(self, *args):
        _start = timestamp()
        try:
            records = [self.fetch(*args)] if args and not isinstance(args[0], Record) else args     # noqa
            for record in records:
                if record._mark is INSERT:
                    raise exc.RecordMarkedForInsertion(record)
                elif record._vsn < 0:
                    raise exc.DeletedRecord(record)
                elif record._vsn == 0:
                    raise exc.UnstoredRecord(record)
                record._mark = DELETE
                self._dirty[record._store].add(record)
        finally:
            logger.debug("%s %0.6f delete %d" % (self._txn, timestamp() - _start, len(records)))    # noqa

    def validate(self, record):
        _start = timestamp()
        try:
            validator = get_validator(record._model)
            if validator:
                errors = validator(record)
                if errors:
                    raise exc.RecordValidationError(record, errors)
        finally:
            logger.debug("%s %0.6f validate %s" % (self._txn, timestamp() - _start, record._model))    # noqa
