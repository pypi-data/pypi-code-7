# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from dk.collections import pset

import pymssql
if pymssql.__version__ >= '2':
    quote_data = pymssql._mssql.quote_data   # pylint:disable=W0212
elif pymssql.__version__ < '2':
    quote_data = pymssql._mssql._quote_data  # pylint:disable=W0212

SQL_STMTS = []

DEBUG = True
if DEBUG:
    logging.basicConfig(level=logging.WARNING)
    #logging.basicConfig(level=logging.DEBUG)


def columns(cursor):
    "Return the column names from the cursor."
    return [d[0] for d in cursor.description]


def quote(val):
    "Quote value for insertion into database."
    # desperately do not want to implement this myself...
    qv = quote_data(val)
    if qv[0] == qv[-1] == "'":
        qv = qv[1:-1]
    return qv


def quote_sql(s):
    return quote_data(s)


def quote_list(lst):
    return ', '.join(map(str, map(quote_sql, lst)))
    

# def dict2pset(d):
#     res = pset()
#     indices = set(range(len(d) / 2))
#     for key in d:
#         if key not in indices:
#             pass

# ########################################################################

# def utf8strings(val):
#     if type(val) not in (str, unicode):
#         return val
#     if isinstance(val, unicode):
#         return val.encode('u8')
#     try:
#         return val.decode('l1').encode('u8')
#     except:
#         return val

########################################################################

_pymssqltypes = {
    1: 'STRING',
    2: 'BINARY',
    3: 'NUMBER', 
    4: 'DATETIME',
    5: 'DECIMAL',
    }
    

class dbcursor(object):
    """Proxy for native database cursor class.
    """
    def __init__(self, cursor, db2py, py2db, db):
        self._cursor = cursor
        self._db2py = db2py
        self._py2db = py2db
        self._db = db

    def __getattr__(self, attr):
        return getattr(self._cursor, attr)

    def _set_types(self, description):
        if self._db == 'mssql':
            self._types = [_pymssqltypes[d[1]] for d in description]
        elif self._db == 'mysql':
            self._types = [None] * len(description)
        else:
            self._types = [None] * len(description)

    def callproc(self, procname, args=None):
        "Call a stored proc."
        # pymssql Issue 56 (no unicode in callproc args).
        # (http://code.google.com/p/pymssql/issues/detail?id=56)
        if isinstance(args, tuple) and len(args) > 0:
            newargs = []
            for arg in args:
                if isinstance(arg, unicode):
                    newargs.append(str(arg))
                else:
                    newargs.append(arg)
            args = tuple(newargs)

        procname = 'exec ' + procname
        if args:
            argmarkers = ['%s'] * len(args)
            procname += ' ' + ', '.join(argmarkers)

        return self._execute(self._cursor.execute, procname, args)

    def execute(self, _sql, args=None):
        "Execute statment."
        return self._execute(self._cursor.execute, _sql, args)

    def _execute(self, execfn, _sql, args=None):
        if settings.DEBUG or settings.TESTING:
            SQL_STMTS.append((_sql, args))
        sql = str(_sql)  # _sql could be SafeUnicode :-(
        try:
            #start = time.time()
            if args is None or (isinstance(args, tuple) and len(args) == 0):
                retval = execfn(sql)
            elif isinstance(args, tuple):
                if len(args) == 1:
                    args = self._py2db(args)
                    retval = execfn(sql, args)
                else:
                    args = tuple([self._py2db(a) for a in args])
                    retval = execfn(sql, args)
            else:
                args = self._py2db(args)
                retval = execfn(sql, args)

        except:
            logging.exception(args)
            logging.exception(sql)
            raise

        description = self._cursor.description
        if description:
            self._columns = [d[0] for d in description]
            self._set_types(description)

        return retval

    def fetchvalue(self):
        "Fetch a single value."
        rec = self._cursor.fetchone()
        if rec is None:
            return None
        t, v = self._types[0], rec[0]
        return self._db2py(v, t)

    def fetchone(self):
        "Fetch one record"
        rec = self._cursor.fetchone()
        if rec is None:
            return None

        #return self._wrap_record(rec)

        res = pset()
        
        for k, t, v in zip(self._columns, self._types, rec):
            res[k] = self._db2py(v, t)
        return res

    def fetchall(self):
        "Fetch entire resultset."
        recs = self._cursor.fetchall()
        result = []
        for rec in recs:
            p = pset()
            for k, t, v in zip(self._columns, self._types, rec):
                p[k] = self._db2py(v, t)
            result.append(p)
        return result

########################################################################


def ident(x, *_rest):
    "lambda x.x"
    return x


class dbconnection(object):
    def __init__(self, cn, db2py=ident, py2db=ident, database='mssql'):
        self._cn = cn
        self._db2py = db2py
        self._py2db = py2db
        self._db = database

    #def __del__(self):
    #    if self._cn is not None:
    #        del self._cn

    def close(self):
        if settings.DEBUG or settings.TESTING:
            SQL_STMTS.append(('CLOSE CONNECTION', ()))
        self._cn.close()
        self._cn = None

    def reset(self):
        if settings.DEBUG or settings.TESTING:
            SQL_STMTS.append(('exec sp_reset_connection', ()))
        # would have been nice to be able to use sp_reset_connection...
        # self.execute("exec sys.sp_reset_connection")
        # ..instead we take a pointer from sqlalchemy:
        self._cn.rollback()

    def commit(self):
        if settings.DEBUG or settings.TESTING:
            SQL_STMTS.append(('COMMIT', ()))
        self._cn.commit()
        #self.reset()
        
    def __getattr__(self, attr):
        return getattr(self._cn, attr)

    def quote(self, v):
        """Quote ``v``, so that it's suitable for direct inclusion into a sql
           statement.
        """
        return quote_sql(v)

    def cursor(self):
        "Return a wrapped cursor."
        return dbcursor(self._cn.cursor(), self._db2py, self._py2db, self._db)

    def execute(self, sql, *args):
        "Execute a sql statement that doesn't return a resultset."
        c = self.cursor()
        if settings.DEBUG or settings.TESTING:
            SQL_STMTS.append((sql, args))
        c.execute(sql, args)

    def fetchvalue(self, sql, *args):
        "Fetch a single value."
        c = self.cursor()
        if settings.DEBUG or settings.TESTING:
            SQL_STMTS.append((sql, args))
        c.execute(sql, args)
        return c.fetchvalue()

    def fetchlist(self, sql, *args):
        "Fetch a list of values."
        c = self.cursor()
        if settings.DEBUG or settings.TESTING:
            SQL_STMTS.append((sql, args))
        c.execute(sql, args)
        return [rec[0] for rec in c.fetchall()]

    def fetchone(self, sql, *args):
        "Fetch one record."
        c = self.cursor()
        if settings.DEBUG or settings.TESTING:
            SQL_STMTS.append((sql, args))
        c.execute(sql, args)
        return c.fetchone()

    def fetchall(self, sql, *args):
        "Fetch all records."
        c = self.cursor()
        if settings.DEBUG or settings.TESTING:
            SQL_STMTS.append((sql, args))
        c.execute(sql, args)
        return c.fetchall()

    def table(self, dbname, tablename, **kw):
        import information_schema
        return information_schema.Table(
            dbname,
            tablename,
            self,
            **kw)
