# -*- coding: utf-8 -*-
import re


def     peewee_overrided_database_init(self, database, **connect_kwargs):
    res = re.search(r'(?P<engine>([a-z0-3]{3,})):\/\/((?P<user>([\S+]{1,})):(?P<passwd>([\S+]{1,}))@(?P<host>([\S+]{1,}))\/|)(?P<name>([\S+]{1,}))', database)
    if res is not None:
        conn_info = res.groupdict()
        self.deferred = database is None
        self.database = conn_info.pop('name', None)
        self.engine = conn_info.pop('engine', '').lower()
        conn_info = {k: v if not v.isdigit() else int(v, 10) for k, v in conn_info.items() if v}
        if self.engine in ('mysql', 'postgresql'):
            self.connect_kwargs = conn_info
        elif self.engine in ('sqlite', 'sqlite3'):
            self.connect_kwargs = {}
        else:
            self.connect_kwargs = connect_kwargs
    else:
        self.deferred = database is None
        self.database = database
        self.connect_kwargs = connect_kwargs
        self.engine = None
