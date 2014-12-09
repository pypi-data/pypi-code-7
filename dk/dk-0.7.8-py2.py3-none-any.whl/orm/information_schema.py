# -*- coding: utf-8 -*-

"""Fetch information from information schema.
"""

# pylint:disable=R0903
# R0903: Too few public methods.


import mssql


class Table(object):
    """Fetch information schema information about table.
    """
    def __init__(self, dbname, tablename, cn, **kw):
        self.dbname = dbname
        self.tablename = tablename

        c = cn.cursor()
        c.execute("""
           select *
           from """ + dbname + """.INFORMATION_SCHEMA.COLUMNS
           where table_name = %s
           order by ordinal_position
           """, (tablename,))

        self.fields = [mssql.MSSqlField(rec, {}, kw.get('utf8', True))
                       for rec in c.fetchall()]
        self.field = dict((f.name, f) for f in self.fields)
