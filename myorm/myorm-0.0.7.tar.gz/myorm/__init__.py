#!/usr/bin/env python
# coding: utf-8

AUTHOR = "Christian Kokoska"

from flask import g

class InvalidFieldName(Exception):
    pass

class NoParameters(Exception):
    pass

def get_order(filter):
    """
    Helper function which provides the order query
    """
    order = ""
    for key, value in filter.items():
        if key == "order_by":
            if value.startswith("-"):
                value = value[1:]
                order = "ORDER BY %s " % (value) + "DESC"
            else:
                order = "ORDER BY %s " % (value) + "ASC"
    return order


def get_objects(cls, filter):
    """
    Helper function to return the fetched values in the right order
    """
    objects = []
    mapped = {}
    for item in cls.adaptor.get_by_filter(filter, cls.tablename, cls.fields.keys()):
        object = cls(*item)
        mapped = zip(cls.fields.keys(), item)
        for item in mapped:
            setattr(object, item[0], item[1])
        objects.append(object)
    return objects


class DbObject(object):
    """
    The class from which the classes in the application inherits
    """
    def __init__(self):
        self.adaptor = None

    @classmethod
    def all(cls, **kwargs):
        filter = "1=1 " + get_order(kwargs)
        return get_objects(cls, filter)

    @classmethod
    def get(cls, *args, **kwargs):
        if not kwargs:
            raise NoParameters('No parameters provided')
        return cls.filter(*args, **kwargs)[0]

    @classmethod
    def filter(cls, **kwargs):
        if not kwargs:
            raise NoParameters('No parameters provided')

        filter = cls.adaptor.get_filter(tablename=cls.tablename,
                                        fields=cls.fields,
                                        filter=kwargs)

        return get_objects(cls, filter)

    @classmethod
    def create(cls, *args, **kwargs):
        """
        This method can be called to create an object

        :param class: The class which calls this method
        :return: The freshly created object
        """
        return cls.adaptor.create(cls, cls.tablename, cls.fields.keys(), kwargs)

    def save(self, *args, **kwargs):
        """
        Function can be called to create or update an object
        """
        if self.id:
            self.update(self.tablename, self.fields.keys(), kwargs)
        else:
            for fieldname in self.fields.keys():
                kwargs[fieldname] = getattr(self, fieldname)
            self.create(self, self.tablename, self.fields.keys(), **kwargs)

    def update(self, *args, **kwargs):
        return self.adaptor.update(self.tablename, self.fields.keys(), self)

    def delete(self, *args, **kwargs):
        return self.adaptor.delete(self.tablename, self)

    @classmethod
    def pure(cls, *args):
        """
        Function which can be used to select items from the database by pure SQL

        :param query: A pure SQL select query
        :return: An object of the calling class
        """
        return [cls(*item) for item in cls.adaptor.get_by_sql(args[0])]

    @classmethod
    def raw(cls, query, *args):
        """
        Executes a query
        """
        con = cls.adaptor.get_connection()
        cur = con.cursor()
        cur.execute(query)
        try:
            fetch = cur.fetchall()
        except:
            fetch = None
        con.commit()
        return fetch

    @classmethod
    def create_table(cls):
        """
        Helper function to create tables based on their fieldnames and tablename
        """
        return cls.adaptor.create_table(cls)


class Adaptor():
    """
    Class to provide some common methods which can be used by more than one
    child adaptor
    """

    def get_filter(self, **kwargs):
        fields = kwargs['fields']
        tablename = kwargs['tablename']
        filter = kwargs['filter']

        filters = []
        order = ""
        limit = ""

        for key, value in filter.iteritems():
            if key.split('__')[0] == "max":
                key_value = self.get_key_value(key.split('__')[1], value, tablename, fields)
                filters.append("%s<=%s" % key_value)

            elif key.split('__')[0] == "min":
                key_value = self.get_key_value(key.split('__')[1], value, tablename, fields)
                filters.append("%s>=%s" % key_value)

            elif key.split('__')[0] == "not":
                key_value = self.get_key_value(key.split('__')[1], value, tablename, fields)
                filters.append("%s!=%s" % key_value)

            elif key == "order_by":
                continue

            elif key == "limit":
                limit = " LIMIT %s" % value

            else:
                key_value = self.get_key_value(key, value, tablename, fields)
                filters.append('%s=%s' % key_value)

        filter = (" AND ").join(filters)
        if not filter:
            filter = "1=1"
        filter += " " + get_order(kwargs['filter']) + limit
        return filter

    def get_key_value(self, key, value, *args):
        tablename = args[0]
        fields = args[1]
        quotes = ['char', 'date']
        if fields[key] in quotes:
            value = "'%s'" % value
        return (key, value)

    def update(self, tablename, fieldnames, *args):
        _object = args[0]
        settings = ""
        for fieldname in fieldnames:
            settings += ", " + fieldname + "=%s"
        settings = settings[2:]

        query = "UPDATE %s SET %s WHERE id = %%s" % (tablename, settings)

        values = []
        for fieldname in fieldnames:
            values.append(getattr(_object, fieldname))
        values.append(_object.id)

        con = self.get_connection()
        con.cursor().execute(query, values)
        con.commit()

    def delete(self, tablename, *args):
        _object = args[0]
        query = "DELETE FROM %s WHERE id=%%s" % (tablename)
        con = self.get_connection()
        con.cursor().execute(query, [_object.id])
        con.commit()


class PostgreSQLAdaptor(Adaptor):

    def __init__(self, host, database, username, password):
        self.host = host
        self.database = database
        self.username = username
        self.password = password

    def get_filter(self, **kwargs):
        fields = kwargs['fields']
        tablename = kwargs['tablename']
        filter = kwargs['filter']

        filters = []
        order = ""
        limit = ""

        for key, value in filter.iteritems():
            if key.split('__')[0] == "max":
                key_value = self.get_key_value(key.split('__')[1], value, tablename, fields)

                filters.append("%s<=%s" % key_value)
            elif key.split('__')[0] == "min":
                key_value = self.get_key_value(key.split('__')[1], value, tablename, fields)

                filters.append("%s>=%s" % key_value)
            elif key == "order_by":
                continue
            elif key == "limit":
                limit = " LIMIT %s" % value
            else:
                key_value = self.get_key_value(key, value, tablename, fields)
                filters.append('"%s"=%s' % key_value)
        filter = (" AND ").join(filters)
        if not filter:
            filter = "1=1"
        filter += " " + get_order(kwargs['filter']) + limit
        return filter

    def get_connection(self):
        import psycopg2
        psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
        con = psycopg2.connect(host=self.host,
                               database=self.database,
                               user=self.username,
                               password=self.password)
        return con

    def get_by_sql(self, query, *args):
        cur = self.get_connection().cursor()
        cur.execute(query)
        return cur.fetchall()

    def get_by_filter(self, filter, *args):
        tablename = args[0]
        fieldnames = args[1]
        key_string = ""

        for item in fieldnames:
            key_string += '"%s", ' %  item
        key_string = key_string[:-2]

        query = "SELECT %s FROM %s WHERE %s" % (key_string,
                                                tablename,
                                                filter)
        return self.get_by_sql(query, *args)

    def create(self, cls, tablename, fieldnames, *args, **kwargs):
        empty_fields = set(fieldnames)
        field_values = {}

        for key, value in args[0].iteritems():
            if key not in fieldnames:
                raise InvalidFieldName
            else:
                empty_fields -= set([key])
                field_values[key] = value

        for key in empty_fields:
            field_values[key] = None

        if field_values['id'] == None:
            field_values.pop('id')
            fieldnames.remove('id')

        key_string = ""
        for item in field_values.keys():
            key_string += '"%s", ' %  item
        key_string = key_string[:-2]

        query = "INSERT INTO %s (%s) VALUES (%s) RETURNING id" % (
                                       tablename,
                                       key_string,
                                       ', '.join(['%s'] * len(fieldnames)))

        fieldnames.insert(0, 'id')

        con = self.get_connection()
        cursor = con.cursor()
        cursor.execute(query, field_values.values())
        _id = cursor.fetchone()
        con.commit()
        return cls.get(id=_id[0])

    def create_table(self, cls):
        fields = ""
        for key, value in cls.fields.items():
            if key == 'id':
                fields += 'id SERIAL PRIMARY KEY, '
            if value == 'char':
                fields += '"%s" VARCHAR(200) DEFAULT NULL, ' % key
            if value == 'int' and not key == 'id':
                fields += '"%s" INT DEFAULT 0, ' % key
            if value == 'text':
                fields += '"%s" TEXT DEFAULT NULL, ' % key
            if value == 'bool':
                fields += '"%s" BOOLEAN, ' % key
            if value == 'date':
                fields += '"%s" TIMESTAMP DEFAULT NULL, ' % key

        query = """CREATE TABLE IF NOT EXISTS %s (%s)""" % (cls.tablename,
                                                            fields[:-2])
        cls.raw(query)
        return True


class MySQLAdaptor(Adaptor):

    def __init__(self, host, database, username, password):
        self.host = host
        self.database = database
        self.username = username
        self.password = password

    def get_connection(self):
        import MySQLdb
        con = MySQLdb.connect(host=self.host,
                              db=self.database,
                              user=self.username,
                              passwd=self.password,
                              use_unicode=True,
                              charset='utf8')
        return con

    def get_by_sql(self, query, *args):
        cur = self.get_connection().cursor()
        cur.execute(query)
        return cur.fetchall()

    def get_by_filter(self, filter, *args):
        tablename = args[0]
        fieldnames = args[1]
        query = "SELECT %s FROM %s WHERE %s" % (', '.join(fieldnames),
                                                tablename,
                                                filter)
        return self.get_by_sql(query, *args)

    def get_last_inserted_id(self, con):
        cur = con.cursor()
        cur.execute("""SELECT last_insert_id()""")
        return cur.fetchone()[0]

    def create(self, cls, tablename, fieldnames, *args, **kwargs):
        empty_fields = set(fieldnames)
        field_values = {}

        for key, value in args[0].iteritems():
            if key not in fieldnames:
                raise InvalidFieldName
            else:
                empty_fields -= set([key])
                field_values[key] = value

        for key in empty_fields:
            field_values[key] = None

        query = "INSERT INTO %s (%s) VALUES (%s)" % (
                                            tablename,
                                            ', '.join(field_values.keys()),
                                            ', '.join(['%s'] * len(fieldnames)))

        con = self.get_connection()
        con.cursor().execute(query, field_values.values())
        con.commit()
        return cls.get(id=self.get_last_inserted_id(con))

    def create_table(self, cls):
        fields = ""
        pk = ""
        for key, value in cls.fields.items():
            if key == 'id':
                fields += "id INT NOT NULL AUTO_INCREMENT, "
                pk = ", PRIMARY KEY (id)"
            if value == 'char':
                fields += "%s VARCHAR(200) DEFAULT NULL, " % key
            if value == 'int' and not key == 'id':
                fields += "%s INT DEFAULT 0, " % key
            if value == 'text':
                fields += "%s TEXT DEFAULT NULL, " % key
            if value == 'bool':
                fields += "%s BOOLEAN, " % key
            if value == 'date':
                fields += "%s DATETIME DEFAULT NULL, " % key
        query = """CREATE TABLE IF NOT EXISTS %s (%s %s)""" % (cls.tablename,
                                                              fields[:-2],
                                                              pk)
        cls.raw(query)
        return True


class SQLiteAdaptor(Adaptor):

    def __init__(self, database):
        self.database = database

    def get_connection(self):
        import sqlite3
        con = sqlite3.connect(self.database)
        return con

    def get_key_value(self, key, value, *args):
        tablename = args[0]
        fields = args[1]
        if fields[key] == 'bool':
            if value:
                value = 1
            else:
                value = 0
        if fields[key] == 'char':
            value = "'%s'" % value
        return (key, value)

    def get_by_sql(self, query, *args):
        cur = self.get_connection().cursor()
        cur.execute(query)
        return cur.fetchall()

    def get_by_filter(self, filter, *args):
        tablename = args[0]
        fieldnames = args[1]
        query = "SELECT %s FROM %s WHERE %s" % (', '.join(fieldnames),
                                                tablename,
                                                filter)
        return self.get_by_sql(query, *args)

    def get_last_inserted_id(self, con):
        cur = con.cursor()
        cur.execute("""SELECT last_insert_rowid()""")
        return cur.fetchone()[0]

    def create(self, cls, tablename, fieldnames, *args, **kwargs):
        empty_fields = set(fieldnames)
        field_values = {}

        for key, value in args[0].iteritems():
            if key not in fieldnames:
                raise InvalidFieldName
            else:
                empty_fields -= set([key])
                field_values[key] = value

        for key in empty_fields:
            field_values[key] = None

        query = "INSERT INTO %s (%s) VALUES (%s)" % (
                                       tablename,
                                       ', '.join(field_values.keys()),
                                       ', '.join(['?'] * len(fieldnames)))

        values = []
        for value in field_values.values():
            values.append(value)

        con = self.get_connection()
        con.cursor().execute(query, values)
        con.commit()
        return cls.get(id=self.get_last_inserted_id(con))

    def update(self, tablename, fieldnames, *args):
        _object = args[0]

        settings = ""
        for fieldname in fieldnames:
            settings += ", " + fieldname + "=?"
        settings = settings[2:]

        values = []
        for fieldname in fieldnames:
            values.append(str(getattr(_object, fieldname)))

        query = "UPDATE %s SET %s WHERE id = %s" % (tablename, settings, _object.id)

        con = self.get_connection()
        con.cursor().execute(query, values)
        con.commit()

    def delete(self, tablename, *args):
        _object = args[0]
        query = "DELETE FROM %s WHERE id=?" % (tablename)
        con = self.get_connection()
        con.cursor().execute(query, [_object.id])
        con.commit()

    def create_table(self, cls):
        fields = ""
        for key, value in cls.fields.items():
            if key == 'id':
                fields += "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            if value == 'char':
                fields += "%s VARCHAR(200) DEFAULT NULL, " % key
            if value == 'int' and not key == 'id':
                fields += "%s INTEGER DEFAULT 0, " % key
            if value == 'text':
                fields += "%s TEXT DEFAULT NULL, " % key
            if value == 'bool':
                fields += "%s BOOLEAN, " % key
            if value == 'date':
                fields += "%s TIMESTAMP DEFAULT NULL, " % key

        query = """CREATE TABLE IF NOT EXISTS %s (%s)""" % (cls.tablename, fields[:-2])
        cls.raw(query)
        return True


class MyDbAdaptor(Adaptor):
    """
    Pet project
    """

    def __init__(self, database):
        self.database = database

    def get_connection(self):
        import db_driver
        con = db_driver.connect(self.database)
        return con

    def get_key_value(cls, key, value, *args):
        tablename = args[0]
        fields = args[1]
        list = ['int', 'date', 'bool']
        if fields[key] in list:
            value = "'%s'" % value

        if fields[key] == 'char':
            value = "'%s'" % value
        return (key, value)

    def get_by_sql(self, query, *args):
        con = self.get_connection()
        return con.execute(query)

    def get_by_filter(self, filter, *args):
        tablename = args[0]
        fieldnames = args[1]
        query = "SELECT %s FROM %s WHERE %s" % (', '.join(fieldnames),
                                                tablename,
                                                filter)
        return self.get_by_sql(query, *args)

    def update(self, tablename, fieldnames, *args):
        _object = args[0]
        settings = ""
        for fieldname in fieldnames:
            settings += ", " + fieldname + "=%s"
        settings = settings[2:]

        query = "UPDATE %s SET %s WHERE id=%%s" % (tablename, settings)

        values = []
        for fieldname in fieldnames:
            values.append(getattr(_object, fieldname))
        values.append(_object.id)

        con = self.get_connection()
        con.execute(query % tuple(values))

    def create(self, cls, tablename, fieldnames, *args, **kwargs):
        empty_fields = set(fieldnames)
        field_values = {}

        for key, value in args[0].iteritems():
            if key not in fieldnames:
                raise InvalidFieldName
            else:
                empty_fields -= set([key])
                field_values[key] = value

        for key in empty_fields:
            field_values[key] = None

        query = "INSERT INTO %s (%s) VALUES (%s)" % (
                                       tablename,
                                       ', '.join(field_values.keys()),
                                       ', '.join(['%s'] * len(fieldnames)))

        values = []
        for value in field_values.values():
            values.append(value)

        con = self.get_connection()
        return cls.get(id=con.execute(query % tuple(values)))

    def delete(self, tablename, *args):
        _object = args[0]
        query = "DELETE FROM %s WHERE id=%s" % (tablename, _object.id)
        con = self.get_connection()
        con.execute(query)
