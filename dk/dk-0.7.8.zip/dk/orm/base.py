# -*- coding: utf-8 -*-

"""This file defines the runtime environment for the orm (and should perhaps be
   renamed runtime.py..?)
"""

# pylint:disable=W0622,W0611
# W0622 redefining Warning (should be available from module)
# W0611 unused quote_sql (ditto)

import operator
import datetime
import textwrap

from dk.collections import pset

from .qobj import Q
from .marker import marker

# pylint: disable=R0902,W0201,W0212,R0903
class OrmMeta(object):
    "Mimic core.modelmeta.info() behavior."
    def __init__(self, cls):
        self.is_model = False
        self.is_orm = True
        self.cls = cls
        self.name = cls.__name__
        self.db_table = cls._dbtable
        self.db_table_alias = cls._prefix
        self.module_name = cls.__module__
        self.primary_keys = cls._pkeys
        self.fields = self.metafields
        self.fieldnames = list(self.metafields.keys())

        self.list_display = []
        self.search_fields = [f for f, _ in self.fields
                              if self.metafields[f].internal_type in (
                                 unicode, str, int, long, bool, datetime.date,
                                 datetime.datetime)]
        self.list_per_page = 12
        
        self.field_info = pset()
        for fname in cls._fields:
            self.field_info[fname] = cls._metafields[fname]

    @property
    def metafields(self):
        "Return a cached version of the class' metafields."
        if not hasattr(self, '_metafields'):
            tmp = [(f.position, f) for f in self.cls._metafields.values()]
            tmp.sort()
            self._metafields = pset()
            for _, f in tmp:
                self._metafields[f.name] = f
        return self._metafields
        
    def __repr__(self):
        from dk.modelinfo import shorten_line
        res = ['\nclass %s:' % self.cls.__name__]
        attrs = [
            shorten_line('name', self.name),
            shorten_line('db_table', self.db_table),
            shorten_line('db_table_alias', self.db_table_alias),
            shorten_line('module_name', self.module_name),
            shorten_line('list_display', self.list_display),
            shorten_line('search_fields', self.search_fields),
            shorten_line('list_per_page', self.list_per_page),
            shorten_line('fields', self.fieldnames),
            #pretty_line('field_layout', self.field_layout),
            ]

        return '\n'.join(res + attrs)


def std_verbose_name(n):
    "Title case with spaces rather than underlines."
    parts = [v.title() for v in n.split('_')]
    return u' '.join(parts)
    

def identity(x):
    "id(x) == x (fixed point, etc., etc.)"
    return x


def tsqldate2date(uc):
    """Convert from a tsql (real) date value.
    """
    if not uc:
        return uc
    y, m, d = uc.split('-')
    return datetime.date(int(y), int(m, 10), int(d, 10))


def date2tsqldate(d):
    """Convert a date to a tsql (real) date.
    """
    return d.strftime("%Y-%02m-%02d")


def datetime2date(dt):
    """Extract the date part of the datetime. Used in autoconversion when
       reading/writing to the database.
    """
    if dt:
        return dt.date()
    else:
        return None


def datetime2time(dt):
    """Extract the time part of the datetime. Used in autoconversion when
       reading/writing to the database.
    """
    return dt.time()


def date2datetime(d):
    """Create a datetime from the date (time == midnight).
    """
    return datetime.datetime(d.year, d.month, d.day)


def time2datetime(t):
    """Create a datetime from a time value (date == January 1, 1900).
       This is necessary because tsql doesn't (historically) have a time type.
    """
    return datetime.datetime(1900, 1, 1, t.hour, t.minute, t.second)


def yesno2bool(v):
    "Interpret the human-readable text v into a boolean."
    if not v:
        return False
    if str(v).lower() in ('j', 'ja', 'y', 'yes'):
        return True
    elif str(v).lower() in ('n', 'nei', 'no'):
        return False
    else:
        return None


def scoreband2bool(s):
    "Interpret score_band_title string as a bool representing pass/fail."
    return s.lower() in [u'bestått', u'pass']


def bool2yesno(v):
    "Convert bool to yes/no."
    return 'yes' if v else 'no'


def bool2janei(v):
    "Convert bool to ja/nei."
    return 'ja' if v else 'nei'


class FieldMeta(object):
    "Meta data for orm fields."

    # pylint:disable=R0913,R0914,W0621
    def __init__(self, name="",
                 dbname="",
                 dbtype='varchar',
                 position=0,
                 nullable=True,
                 max_length=None,
                 default=None, precision=None, scale=None,
                 encoding='None',
                 pytype=unicode,
                 pk=False,
                 marker='%s',
                 uitype=None,
                 verbose_name=None, convert=False, py2db=None, utf8=True):
        # ensure that at least one of name, dbname are strings.
        self.name = dbname.lower() if name == "" else name
        self.dbname = name.lower() if dbname == "" else dbname

        self.verbose_name = verbose_name or std_verbose_name(self.dbname)

        self.dbtype = dbtype
        self.position = position
        self.nullable = nullable
        self.max_length = max_length
        self.default = default
        self.precision = precision
        self.scale = 0 if scale is None and isinstance(self.precision, int) else scale
        self.encoding = encoding
        self.pytype = int if self.dbtype in ("int", "smallint") else pytype
        self.internal_type = pytype
        self.pk = pk
        self.marker = "%d" if self.pytype is int else marker
        self.convert = convert
        self.py2db = py2db or identity
        self.uitype = uitype or dbtype
        self.utf8 = utf8
        self.rel = False

    def get_internal_type(self):
        """Cf. Django's get_internal_type.
        """
        return self.dbtype

    def selector(self, prefix=''):
        """Return the text needed to select this field (only what goes
           after 'select').
        """
        if prefix:
            prefix += '.'
        if self.utf8 and self.dbtype == 'varchar':
            res = 'dbo.utf2latin(%s%s) as %s' % (prefix, self.dbname, self.name)
        else:
            res = '%s%s as %s' % (prefix, self.dbname, self.name)
        return res

    def __repr__(self):
        return textwrap.dedent('''\
        FieldMeta(
            name = %s,
            dbname = %s,
            verbose_name = %s,
            dbtype = %s,
            position = %s,
            nullable = %s,
            max_length = %s,
            default = %s,
            precision = %s,
            scale = %s,
            encoding = %s,
            pytype = %s,
            internal_type = %s,
            pk = %s,
            marker = %s
        )''' % tuple(map(repr, [  # pylint:disable=W0141
            self.name, self.dbname, self.verbose_name, self.dbtype,
            self.position, self.nullable, self.max_length, self.default,
            self.precision, self.scale, self.encoding, self.pytype,
            self.internal_type, self.pk, self.marker])))
  

def update_clause(items):
    """Return assignment text for an update statement where the field/value
       pairs in items are being updated.
    """
    res = []
    for k, v in items:
        res.append('%s = %s' % (k, marker(v)))
    return ', '.join(res)

    
def where_clause(items):
    """Return where clause text for the key/value pairs in items.
    """
    res = []
    for k, v in items:
        res.append('%s = %s' % (k, marker(v)))
    return ' and '.join(res)


def where_parameters(items):
    "Return a tuple of the field names that are being changed."
    return tuple(v[1] for v in items)


class RecordList(list):
    "A list of Record (orm) objects."
    def remove(self, key):
        "Emulate orm.remove()."
        self[key].remove()
        del self[key]

    def count(self):
        "Emulate orm.count()."
        return len(self)
    
    def order_by(self, *args):
        "Emulate orm.order_by()."
        self.sort(key=lambda v: tuple(getattr(v, a) for a in args))
        return self

    def get(self, **fields):
        "Emulate orm.get()."
        tmp = self.filter(**fields)
        if len(tmp) != 1:
            raise ValueError('Did not return 1 object, returned: %d' % len(tmp))
        return tmp[0]

    def join(self, other, on=None, default=None):
        """Efficiently fetch a resultset from ``other`` and join it with
           ourselves.

           Usage::

               results = dk.AResult.select_list(test_center='N-042')
               results.join(dk.GParticipant,
                            on=dict(participant='participant_name'))

           if the ``on`` clause is not specified, the primary key of both
           ``self`` and ``other`` is used.
        """
        if not self:
            return
        if on is None:
            on = dict(zip(self[0]._pkeys, other._pkeys))

        # extract keys
        assert len(on) == 1
        lhs_key = on.keys()[0]
        keys = set(getattr(item, lhs_key) for item in self)
        
        rhs_key = on[lhs_key]
        otherlist = other.list(
            other.objects.filter(**{rhs_key + '__in': list(keys)})
            )
        
        rhs = dict((getattr(item, rhs_key), item) for item in otherlist)
        for item in self:
            setattr(item,
                    other.__name__.lower(),
                    rhs.get(getattr(item, lhs_key), default))

    def filter(self, **fields):
        "Emulate orm.filter()."
        if not fields:
            return self
        
        def _fieldops():
            res = []
            for f, v in fields.items():
                fop = f.split('__')
                if len(fop) == 1:
                    res.append((fop[0], None, v))
                else:
                    res.append((fop[0], fop[1], v))
            return res
        fieldops = _fieldops()

        res = []

        for item in self:
            for field, op, val in fieldops:
                if op is None:  # optimization of most taken path (eq)
                    if not getattr(item, field) == val:
                        break
                    continue
                    
                if not getattr(operator, op)(getattr(item, field), val):
                    break
            else:
                res.append(item)

        return RecordList(res)            


class RecordMeta(object):
    """Imitate Django's Model._meta field.
    """
    def __init__(self):
        pass

    def __get__(self, _instance, cls):
        self.cls = cls
        return self

    def get_all_field_names(self):
        """[Django: Returns a list of all field names that are
           possible for this model (including reverse relation
           names). This is used for pretty printing debugging output
           (a list of choices), so any internal-only field names are
           not included.]

           TODO: make this match docstring (currently only returns direct
                 fields, including all the internal _id fields for fkey
                 relationships (ie. no fkey fields or m2m fields by their
                 traversal names are included).
        """
        return self.cls._fields

    def get_field_by_name(self, fname):
        """[Django: Returns the (field_object, model, direct, m2m),
           where field_object is the Field instance for the given
           name, model is the model containing this field (None for
           local fields), direct is True if the field exists on this
           model, and m2m is True for many-to-many relations.  When
           'direct' is False, 'field_object' is the corresponding
           RelatedObject for this field (since the field doesn't have
           an instance associated with it).]

           TODO: make this match docstring (currently only returns direct
                 fields, including all the internal _id fields for fkey
                 relationships (ie. no fkey fields or m2m fields by their
                 traversal names are included).
        """
        return self.cls._metafields[fname], None, True, False


class RecordMetaclass(type):
    def __init__(cls, name, bases, namespace):
        super(RecordMetaclass, cls).__init__(name, bases, namespace)
        for i, _f in enumerate(namespace.get('_fields', ())):
            namespace['_metafields'][_f].position = i + 1
        for _f in namespace.get('_pkeys', ()):
            namespace['_metafields'][_f].pk = True


class Record(object):
    "Base class for orm objects."
    __metaclass__ = RecordMetaclass

    _dbtable = ""
    _prefix = ""
    _dbcnv = dict(db2py=identity, py2db=identity)
    _pkeys = []
    _meta = RecordMeta()
    _metafields = {}
    update_stmt = ""
    _delete_stmt = ""
    _insert_sproc = ""
    _fields = []
    _initialized = False
    _fromdb = False
    
    def __init__(self):
        self._changed = set()

    @property
    def pk(self):
        if len(self._pkeys) == 1:
            return getattr(self, self._pkeys[0])
        return tuple(getattr(self, k) for k in self._pkeys)

    @classmethod
    def init_from_db(cls, **kw):
        "Initialize from database."
        cvtfields = [mf for mf in cls._metafields.values() if mf.convert]
        for mf in cvtfields:
            name = mf.name
            if name in kw:
                kw[name] = mf.pytype(kw[name])
        obj = cls(**kw)
        obj._fromdb = True
        return obj
    
    def __getstate__(self):
        res = {}
        for field in self._fields:  # pylint:disable=E1101
            try:
                res[field] = getattr(self, field)
            except AttributeError:
                pass
        return res

    __json__ = __getstate__

    def __setstate__(self, state):
        self._cn = None
        self._changed = set()
        
        for field in self._fields:  # pylint:disable=E1101
            if field in state:
                setfn = '_setvalue_' + field
                if hasattr(self, setfn):
                    getattr(self, setfn)(state[field])
                else:
                    setattr(self, field, state[field])
        self._initialized = True

    def __str__(self):
        res = [self.__class__.__name__ + '(']
        res += ['    %(name)s = %(value)r,' % field
                for field in self.field_iter()]
        res.append(')')
        return '\n'.join(res)

    def __repr__(self):
        keys = set(self._pkeys) & set(self._fields)
        if len(keys) == 0:
            return str(self)
        if len(keys) == 1:
            return '%s(%s)' % (self._dbtable, keys.pop())
        
        return self._dbtable + str(tuple([getattr(self, k) for k in keys]))

    @classmethod
    def info(cls):
        "Return meta information about the class."
        return OrmMeta(cls)

    def _get_dbval(self, fieldname):
        return self._metafields[fieldname].py2db(getattr(self, '_' + fieldname))

    def _pk_tuple(self):
        return tuple([self._dbcnv['py2db'](getattr(self, pk))
                      for pk in self._pkeys])

    def _field_values(self):
        return tuple([self._dbcnv['py2db'](getattr(self, f))
                      for f in self._fields])

    @property
    def _manager(self):
        return self.__class__.objects

    def _executesql(self, cn, sql, args, commit=True):  # pylint:disable=R0201
        c = cn.cursor()
        try:
            c.execute(sql, args)
            if commit:
                cn.commit()
        except:
            raise
            # if commit:
            #     cn.rollback()
            # raise

    def save(self, cn=None, commit=True):
        """Save object to database, using connection ``cn``.
        """
        if not self._pkeys:
            raise RuntimeError(
                "Trying to save record, but the table doesn't have "
                "primary keys defined (this can happen if you try to "
                "save to a model of a view without providing a pkey "
                "reference in the .orm file).")

        if not self._fromdb:
            raise ValueError("Trying to save object that has not been read "
                             "from the database, use insert() instead.")
        if self._changed:
            items = []
            for f in self._changed:
                items.append((f, self._get_dbval(f)))
            sql = self.update_stmt.replace('$changed$', update_clause(items))
            args = where_parameters(items) + self._pk_tuple()

            with self._manager.cnpool.connection(cn) as cn:
                self._executesql(cn, sql, args, commit)

            self._changed.clear()

    def remove(self, cn=None, commit=True):
        "Delete from database."
        sql = self._delete_stmt
        args = self._pk_tuple()

        with self._manager.cnpool.connection(cn) as cn:
            self._executesql(cn, sql, args, commit)

    delete = remove

    def insert(self, cn=None, commit=True):
        "Default insert into database, using a storedproc."
        with self._manager.cnpool.connection(cn) as conn:
            c = conn.cursor()
            c.execute(self._insert_sproc, self._field_values())
            try:
                res = c.fetchall()
            except:
                res = None

            if commit:
                conn.commit()

            return res

    def raw_insert(self, cn=None, commit=True):
        """Use an insert stmt to insert all fields that have a value.
           It's up to the user to make sure all key/index requirements
           are fulfilled.
        """
        sql = "insert into %s ($fields$) values ($markers$)" % self._dbtable
        fields = []
        values = []
        markers = []
        for f in self._fields:
            val = getattr(self, f)
            if val is not None:
                fields.append(f)
                dbval = self._dbcnv['py2db'](val)
                values.append(dbval)
                markers.append(marker(dbval))
        if fields:
            sql = sql.replace('$fields$', ', '.join(fields))
            sql = sql.replace('$markers$', ', '.join(markers))

            with self._manager.cnpool.connection(cn) as conn:
                c = conn.cursor()
                c.execute(sql, tuple(values))
                try:
                    res = c.fetchall()
                except:
                    res = None
                if commit:
                    conn.commit()
                return res
        return None

    def field_iter(self):
        "Iterator over all fields/values (useful in templates)."
        for field in self._fields:
            yield {'name': field, 'value': getattr(self, field)}
        return

    @classmethod
    def _select_columns(cls, columns=None, prefix=None):
        if isinstance(columns, basestring):
            raise ValueError(
                "`columns` parameter must be a list, not: %r" % columns)
        if columns is None:
            columns = cls._fields
        if prefix is None:
            prefix = cls._prefix

        cols = [cls._metafields[c].selector(prefix) for c in columns]
        return cols

    @classmethod
    def select(cls, cn=None, columns=None, **kw):
        """Return a single item (fetch_one).
           Returns None if item can't be found (i.e. it doesn't throw a
           DoesNotExist exception).
        """
        items = kw.items()
        cols = cls._select_columns(columns)
        sql = ('select ' +
               ',\n    '.join(cols) +
               ' from %s %s ' % (cls._dbtable, cls._prefix))

        sql += " where " + where_clause(items)
        args = where_parameters(items)

        with cls.objects.cnpool.connection(cn) as cn:
            c = cn.cursor()
            c.execute(sql, args)
            rec = c.fetchone()
            if rec is None:
                return None
            return cls.init_from_db(**rec)._set_partial(columns)

    @classmethod
    def select_list(cls, cn=None, columns=None, **kw):
        """Returns a list of items.  Same as filter, but returns an actual
           list (not a query set).
        """
        items = kw.items()

        cols = cls._select_columns(columns)
        sql = ('select ' +
               ',\n    '.join(cols) +
               ' from %s %s ' % (cls._dbtable, cls._prefix))
        if items:
            sql += " where " + where_clause(items)
        args = where_parameters(items)

        with cls.objects.cnpool.connection(cn) as cn:
            c = cn.cursor()
            c.execute(sql, args)
            res = c.fetchall()
            # Record has no list member (it's a generated class method).
            # (XXX: the list class(es) should perhaps be defined inside
            #       the model class(es)?)
            # pylint:disable=E1101
            return cls.list(cls.init_from_db(**rec)._set_partial(columns)
                            for rec in res)

    @classmethod
    def search(cls, terms=(), query=None, columns=()):
        "Specialized search method."
        if len(columns) == 0:
            raise ValueError("You must define search columns!")
        
        if query is None:
            query = cls.objects.all()

        if len(terms) == 0:
            return query

        for term in terms:
            tmp = Q(**{'%s__icontains' % columns[0]:term})
            for col in columns[1:]:
                tmp |= Q(**{'%s__icontains' % col:term})
            query = query.filter(tmp)

        return query
    
    def _set_partial(self, fields=None):
        # pylint:disable=E0203
        if fields and (set(fields) != set(self._fields)):
            self._partial = True
            self._fields = fields
        return self

    # def _get_cn(self):
    #     if self._cn is None:
    #         raise NoConnection(
    #             'No Connection set on %s object' % self.__class__.__name__)
    #     return self._cn
    #
    # def _set_cn(self, cn):
    #     self._cn = cn
    #
    # def _del_cn(self):
    #     del self._cn
    #     self._cn = None
    #
    # cn = property(_get_cn, _set_cn, _del_cn, "connection")


def join(A, B):
    "Convenience function to join two orm classes."
    
    class JoinClass(Record):
        "Join class."
        _dbtable = [A._dbtable, B._dbtable]
        _prefix = A._prefix + B._prefix
        _fields = A._fields + B._fields
        _pkeys = A._pkeys + B._pkeys
        _partial = False
        _metafields = A._metafields.copy()

        @classmethod
        def info(cls):
            "Emulate baseclass info()."
            return OrmMeta(cls)

    JoinClass._metafields.update(B._metafields)
    return JoinClass
