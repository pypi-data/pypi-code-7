from codex.tornado.datetime import microtime
from pymysql.converters import escape_string
from sqlalchemy import create_engine
from tornado.web import HTTPError

import re

_named_to_pyformat_re = re.compile('\:([a-zA-Z_][a-zA-Z_0-9]*)')
def named_to_pyformat(query, d):
    params = []
    def f(mo):
        params.append(d[mo.group(1)])
        return '%s'
    query = _named_to_pyformat_re.sub(f, query)
    return query, params

class QueryResult:
    def sql(self):
        return self._sql
    def time_elapsed(self):
        return self._time_elapsed

class QueryReadResult(QueryResult):
    def __init__(self, props):
        self._num_rows = props['num_rows']
        self._data = props['data']
        self._fields = props['fields']
        self._time_elapsed = props['benchmark']
        self._sql = props['sql']
        self._data_converted = []

    def num_rows(self):
        return self._num_rows

    def result(self):
        return self._data

    def result_dict(self):
        if not self._data_converted:
            for d in self._data:
                self._data_converted.append(dict(d.items()))
        return self._data_converted

    def fields(self):
        return self._fields

    def row(self, index=0):
        if index > self._num_rows - 1:
            return None
        try:
            return self._data[index]
        except IndexError:
            return None

    def row_dict(self, index=0):
        r = self.row(index)
        if not r:
            return None
        return dict(r.items())

class QueryWriteResult(QueryResult):
    def __init__(self, props):
        self._affected_rows = props['num_rows']
        self._inserted_id = props['inserted_id']
        self._time_elapsed = props['benchmark']
        self._sql = props['sql']

    def affected_rows(self):
        return self._affected_rows

    def inserted_id(self):
        return self._inserted_id

class Query:

    _reserved_identifiers  = ['*']
    _escape_char = '`'
    _like_escape_str = ''
    _like_escape_chr = ''
    _random_keyword = ' RAND()'
    _count_string = 'SELECT COUNT(*) AS '
    _bind_marker = '?'
    _delete_hack = True

    def __init__(self, db):
        self._db = db
        self._reset()

    def _reset(self):
        self._ar_no_escape = []
        self._ar_select = []
        self._ar_distinct = False
        self._ar_from = []
        self._ar_join = []
        self._ar_where = []
        self._ar_like = []
        self._ar_groupby = []
        self._ar_having = []
        self._ar_keys = []
        self._ar_limit = False
        self._ar_offset = False
        self._ar_order = False
        self._ar_orderby = []
        self._ar_set = {}
        self._ar_wherein = []
        self._ar_aliased_tables = []
        self._ar_store_array = []
        self._error = None

    def _from_tables(self, tables):
        if not isinstance(tables, list):
            tables = [tables]
        return '(' + ', '.join(tables) + ')'

    def _compile_select(self, select_override=False):
        sql = ''
        if select_override:
            sql = select_override
        else:
            sql = 'SELECT ' if not self._ar_distinct else 'SELECT DISTINCT '
            if len(self._ar_select) == 0:
                sql += '*'
            else:
                for key, val in enumerate(self._ar_select):
                    no_escape = None if key not in self._ar_no_escape else self._ar_no_escape[key]
                    self._ar_select[key] = self._protect_identifiers(val, False, no_escape)

                sql += ', '.join(self._ar_select)

        if len(self._ar_from) > 0:
            sql += "\nFROM "
            sql += self._from_tables(self._ar_from)

        if len(self._ar_join) > 0:
            sql += "\n"
            sql += "\n".join(self._ar_join)

        if len(self._ar_where) > 0 or len(self._ar_like) > 0:
            sql += "\nWHERE "

        sql += "\n".join(self._ar_where)

        if len(self._ar_like) > 0:
            if len(self._ar_where) > 0:
                sql += "\nAND "
            sql += "\n".join(self._ar_like)

        if len(self._ar_groupby) > 0:
            sql += "\nGROUP BY "
            sql += ', '.join(self._ar_groupby)

        if len(self._ar_having) > 0:
            sql += "\nHAVING "
            sql += "\n".join(self._ar_having)

        if len(self._ar_orderby) > 0:
            sql += "\nORDER BY "
            sql += ', '.join(self._ar_orderby)
            if self._ar_order != False:
                if self._ar_order == 'desc':
                    sql += ' DESC'
                else:
                    sql += ' ASC'

        if self._ar_limit:
            sql += "\n"
            sql = self._limit(sql, self._ar_limit, self._ar_offset)

        return sql

    def _limit(self, sql, limit, offset):
        if not offset:
            offset = ''
        else:
            offset = str(offset)
            offset += ', '
        return sql + 'LIMIT ' + offset + str(limit)

    def _escape_identifiers(self, item):
        if not self._escape_char:
            return item

        escaped_string = ''
        for id in self._reserved_identifiers:
            if item.find('.' + id) >= 0:
                escaped_string = self._escape_char + item.replace('.', self._escape_char + '.')
                return re.sub('['+self._escape_char+']+', self._escape_char, escaped_string)

        if item.find('.') >= 0:
            escaped_string = self._escape_char + item.replace('.', self._escape_char + '.' + self._escape_char) + self._escape_char
        else:
            escaped_string = self._escape_char + item + self._escape_char

        return re.sub('['+self._escape_char+']+', self._escape_char, escaped_string)

    def _protect_identifiers(self, item, prefix_single=False, protect_identifiers=True, field_exists=True):
        if isinstance(item, dict):
            escaped_array = {}
            for k in item.keys():
                escaped_array[self._protect_identifiers(k)] = self._protect_identifiers(item[k])
            return escaped_array

        alias = ''
        item = re.sub('[\t ]+', ' ', item)
        pos = item.find(' ')

        if pos >= 0:
            alias = item[pos:]
            item = item[:-len(alias)]

        if item.find('(') >= 0:
            return item + alias

        if item.find('.') >= 0:
            parts = item.split('.')
            if parts[0] in self._ar_aliased_tables:
                if protect_identifiers:
                    for key, val in enumerate(parts):
                        if val not in self._reserved_identifiers:
                            parts[key] = self._escape_identifiers(val)
                    item = '.'.join(parts)
                return item + alias

            if protect_identifiers:
                item = self._escape_identifiers(item)
            return item + alias

        if protect_identifiers and item not in self._reserved_identifiers:
            item = self._escape_identifiers(item)

        return item + alias

    def _track_aliases(self, table):
        if isinstance(table, list):
            for t in table:
                self._track_aliases(t)
            return
        if table.find(',') >= 0:
            return self._track_aliases(table.split(','))
        if table.find(' ') >= 0:
            table = re.sub('\s+AS\s+', ' ', table, flags=re.IGNORECASE)
            table = table[table.rfind(' '):].strip()
            if table not in self._ar_aliased_tables:
                self._ar_aliased_tables.append(table)

    def select(self, fields='*', escape=None):
        if isinstance(fields, str):
            fields = fields.split(',')

        for field in fields:
            field = field.strip()
            if field != '':
                self._ar_select.append(field)
                self._ar_no_escape.append(escape)

        return self

    def from_table(self, table):
        if not isinstance(table, list):
            table = [table]
        for val in table:
            if val.find(',') >= 0:
                for v in val.split(','):
                    v = v.strip()
                    self._track_aliases(v)
                    self._ar_from.append(self._protect_identifiers(v))
            else:
                val = val.strip()
                self._track_aliases(val)
                self._ar_from.append(self._protect_identifiers(val))
        return self

    def join(self, table, cond, join_type=''):
        if join_type:
            join_type = join_type.strip().upper()
            if join_type not in ['LEFT', 'RIGHT', 'OUTER', 'INNER', 'LEFT OUTER', 'RIGHT OUTER']:
                join_type = ''
            else:
                join_type += ' '

        self._track_aliases(table)
        match = re.search('/([\w\.]+)([\W\s]+)(.+)/', cond)
        if match:
            a = self._protect_identifiers(match.group(1))
            b = self._protect_identifiers(match.group(3))
            cond = a + match.group(2) + b

        self._ar_join.append(join_type + 'JOIN ' + self._protect_identifiers(table, True, True, False) + ' ON ' + cond)
        return self

    def _has_operator(self, value):
        value = value.strip()
        if not re.search("(\s|<|>|!|=|is null|is not null)", value, re.IGNORECASE):
            return False
        return True

    def _escape_str(self, value, like=False):
        if isinstance(value, list):
            for key, val in enumerate(value):
                value[key] = self._escape_str(val, like)
            return value
        value = escape_string(str(value))
        if like:
            value = value.replace('%', "\\%").replace('_', "\\_")
        return value

    def _escape(self, value):
        if isinstance(value, str):
            value = "'" + self._escape_str(value) + "'"
        elif isinstance(value, bool):
            value = 0 if value == False else 1
        elif value is None:
            value = 'NULL'            
        return str(value)

    def _where(self, key, value=None, cond_type='AND ', escape=True):
        if not isinstance(key, dict):
            key = { key : value }
        for k in key.keys():
            v = key[k]
            prefix = '' if len(self._ar_where) == 0 else cond_type
            if v is None and not self._has_operator(k):
                k += ' IS NULL'
            if v is not None:
                if escape:
                    k = self._protect_identifiers(k, False, escape)
                    v = ' ' + self._escape(v)
                if not self._has_operator(k):
                    k += ' = '
            else:
                k = self._protect_identifiers(k, False, escape)
            self._ar_where.append(prefix + k + v)
        return self

    def where(self, key, value=None, escape=True):
        return self._where(key, value, 'AND ', escape)

    def or_where(self, key, value=None, escape=True):
        return self._where(key, value, 'OR ', escape)

    def _where_in(self, key, values, is_not=False, cond_type='AND '):
        if not isinstance(values, list):
            values = [values]
        is_not = ' NOT' if is_not else ''
        for value in values:
            self._ar_wherein.append(self._escape(value))
        prefix = '' if len(self._ar_where) == 0 else cond_type
        where_in = prefix + self._protect_identifiers(key) + is_not + ' IN (' + ', '.join(self._ar_wherein) + ') '
        self._ar_where.append(where_in)
        self._ar_wherein = []
        return self

    def where_in(self, key, values):
        return self._where_in(key, values)

    def or_where_in(self):
        return self._where_in(key, values, False, 'OR ')

    def where_not_in(self, key, values):
        return self._where_in(key, values, True)

    def or_where_not_in(self, key, values):
        return self._where_in(key, values, True, 'OR ')

    def _escape_like_str(self, value):
        return self._escape_str(value, True)

    def _like(self, field, match='', cond_type='AND ', side='both', is_not=''):
        if not isinstance(field, dict):
            field = { field : match }
        for k in field.keys():
            v = field[k]
            k = self._protect_identifiers(k)
            prefix = '' if len(self._ar_like) == 0 else cond_type
            v = self._escape_like_str(v)
            like_statement = ''
            if side == 'none':
                like_statement = prefix + ' ' + k + ' ' + is_not + " LIKE '" + v + "'"
            elif side == 'before':
                like_statement = prefix + ' ' + k + ' ' + is_not + " LIKE '%" + v + "'"
            elif side == 'after':
                like_statement = prefix + ' ' + k + ' ' + is_not + " LIKE '" + v + "%'"
            else:
                like_statement = prefix + ' ' + k + ' ' + is_not + " LIKE '%" + v + "%'"
            self._ar_like.append(like_statement)
        return self

    def like(self, field, match=''):
        return self._like(field, match, 'AND ', 'both')

    def or_like(self, field, match=''):
        return self._like(field, match, 'OR ', 'both')

    def not_like(self, field, match=''):
        return self._like(field, match, 'AND ', 'both', 'NOT')

    def or_not_like(self, field, match=''):
        return self._like(field, match, 'OR ', 'both', 'NOT')

    def like_before(self, field, match=''):
        return self._like(field, match, 'AND ', 'before')

    def or_like_before(self, field, match=''):
        return self._like(field, match, 'OR ', 'before')

    def not_like_before(self, field, match=''):
        return self._like(field, match, 'AND ', 'before', 'NOT')

    def or_not_like_before(self, field, match=''):
        return self._like(field, match, 'OR ', 'before', 'NOT')

    def like_after(self, field, match=''):
        return self._like(field, match, 'AND ', 'after')

    def or_like_after(self, field, match=''):
        return self._like(field, match, 'OR ', 'after')

    def not_like_after(self, field, match=''):
        return self._like(field, match, 'AND ', 'after', 'NOT')

    def or_not_like_after(self, field, match=''):
        return self._like(field, match, 'OR ', 'after', 'NOT')

    def group_by(self, by):
        if isinstance(by, str):
            by = by.split(',')
        for val in by:
            val = val.strip()
            if val != '':
                self._ar_groupby.append(self._protect_identifiers(val))
        return self

    def distinct(self, val=True):
        self._ar_distinct = val
        return self

    def _having(self, key, value='', cond_type='AND ', escape=True):
        if not isinstance(key, dict):
            key = { key : value }
        for k in key.keys():
            v = key[k]
            prefix = '' if len(self._ar_having) == 0 else cond_type
            if escape:
                k = self._protect_identifiers(k)
            if not self._has_operator(k):
                k += ' = '
            if v != '':
                v = ' ' + self._escape(v)
            self._ar_having.append(prefix + k + v)
        return self

    def having(self, key, value='', escape=True):
        return self._having(key, value, 'AND ', escape)

    def or_having(self, key, value='', escape=True):
        return self._having(key, value, 'OR ', escape)

    def order_by(self, orderby, direction=''):
        if direction.lower() == 'random':
            orderby = ''
            direction = self._random_keyword
        elif direction.strip():
            direction = ' ' + direction if direction.strip().upper() in ['ASC', 'DESC'] else ' ASC'
        if orderby.find(',') >= 0:
            temp = []
            for part in orderby.split(','):
                part = part.strip()
                if part not in self._ar_aliased_tables:
                    part = self._protect_identifiers(part)
                temp.append(part)
            orderby = ', '.join(temp)
        elif direction != self._random_keyword:
            orderby = self._protect_identifiers(orderby)

        self._ar_orderby.append(orderby + direction)
        return self

    def limit(self, value, offset=''):
        self._ar_limit = int(value);
        if offset != '':
            self._ar_offset = int(offset)
        return self

    def _compile_binds(self, sql, binds):
        if sql.find(self._bind_marker) < 0:
            return sql
        if not isinstance(binds, list):
            binds = [binds]
        segments = sql.split(self._bind_marker)
        if len(binds) >= len(segments):
            binds = binds[:len(segments) - 1]
        result = segments[0]
        i = 1
        for bind in binds:
            result += self._escape(bind)
            result += segments[i]
            i += 1
        return result

    def _prep_query(self, sql):
        if self._delete_hack:
            if re.search('^\s*DELETE\s+FROM\s+(\S+)\s*$', sql, re.IGNORECASE):
                sql = re.sub('^\s*DELETE\s+FROM\s+(\S+)\s*$', "DELETE FROM \1 WHERE 1=1", sql)
        return sql

    def error(self):
        return self._error

    def _simple_query(self, sql):
        sql = self._prep_query(sql)
        query_result = False
        if not Connection.show_error:
            try:
                query_result = self._db.execute(sql)
                self._error = None
            except Exception as error:
                self._error = error
                self._db.close()
                return False
        else:
            query_result = self._db.execute(sql)
        return query_result

    def _is_write_type(self, sql):
        if not re.search('^\s*"?(SET|INSERT|UPDATE|DELETE|REPLACE|CREATE|DROP|TRUNCATE|LOAD DATA|COPY|ALTER|GRANT|REVOKE|LOCK|UNLOCK)\s+', sql, re.IGNORECASE):
            return False;
        return True;

    def _query(self, sql, binds=False):
        if not sql:
            # TODO: Create logging
            return False
        if binds:
            sql = self._compile_binds(sql, binds)

        # TODO : Saving queries for profiling
        (sm, ss) = microtime().split(' ')
        result = self._simple_query(sql)
        if not result:
            return False
        (em, es) = microtime().split(' ')

        props = {
            'benchmark' : (float(em) + float(es)) - (float(sm) + float(ss)),
            'num_rows' : result.rowcount,
            'sql' : sql
        }
        return_object = False
        if self._is_write_type(sql):
            props['inserted_id'] = result.lastrowid
            return_object = QueryWriteResult(props)
        else:
            props['data'] = result.fetchall()
            props['fields'] = result.keys()
            return_object = QueryReadResult(props)

        result.close()
        del result
        return return_object

    def count_all_results(self, table=''):
        if table != '':
            self._track_aliases(table)
            self.from_table(table)
        sql = self._compile_select(self._count_string + self._protect_identifiers('numrows'))
        query = self._query(sql)
        if query.num_rows() == 0:
            return 0
        return int(query.row()['numrows'])

    def count_all(self, table):
        if not table:
            return 0
        query = self._query(self._count_string + self._protect_identifiers('numrows') + ' FROM ' + self._protect_identifiers(table, False, True, False))
        if query.num_rows() == 0:
            return 0
        return int(query.row()['numrows'])

    def set(self, key, value='', escape=True):
        if not isinstance(key, dict):
            key = { key : value }
        for k in key.keys():
            v = key[k]
            if not escape:
                self._ar_set[self._protect_identifiers(k)] = str(v)
            else:
                self._ar_set[self._protect_identifiers(k, False, True)] = self._escape(v)
        return self

    def _insert(self, table, keys, values):
        return "INSERT INTO " + table + " (" + ', '.join(keys) + ") VALUES (" + ', '.join(values) + ")"

    def insert(self, table='', data=None):
        if data is not None:
            self.set(data)

        if len(self._ar_set) == 0:
            if Connection.show_error:
                raise HTTPError(500, 'Use Query.set to sql write data')
            return False

        if not table:
            if len(self._ar_from) == 0:
                if Connection.show_error:
                    raise HTTPError(500, 'Must set table name')
                return False
            table = self._ar_from[0]

        sql = self._insert(self._protect_identifiers(table, True, True, False), self._ar_set.keys(), self._ar_set.values())
        return self._query(sql)

    # def insert_batch(self):
    #     pass

    def _update(self, table, values, where, orderby=[], limit=False):
        valstr = []
        for key in values.keys():
            valstr.append(key + ' = ' + values[key])

        limit = '' if not limit else ' LIMIT ' + limit
        orderby = '' if not len(orderby) else ' ORDER BY ' + ', '.join(orderby)

        sql = 'UPDATE ' + table + ' SET ' + ', '.join(valstr)
        sql += ' WHERE ' + ' '.join(where) if where != '' and len(where) >= 1 else ''
        sql += orderby + limit
        return sql

    def update(self, table='', data=None, where=None, limit=None):
        if data is not None:
            self.set(data)

        if len(self._ar_set) == 0:
            if Connection.show_error:
                raise HTTPError(500, 'Use Query.set to sql write data')
            return False

        if not table:
            if len(self._ar_from) == 0:
                if Connection.show_error:
                    raise HTTPError(500, 'Must set table name')
                return False
            table = self._ar_from[0]

        if where:
            self.where(where)

        if limit:
            self.limit(limit)

        sql = self._update(self._protect_identifiers(table, True, True, False), self._ar_set, self._ar_where, self._ar_orderby, self._ar_limit)
        return self._query(sql)

    # def update_batch(self):
    #     pass

    def get(self, table='', limit=None, offset=None):
        if table:
            self._track_aliases(table)
            self.from_table(table)

        if limit:
            self.limit(limit, offset)

        sql = self._compile_select()
        return self._query(sql)

    def _delete(self, table, where=[], like=[], limit=False):
        conditions = ''
        if len(where) > 0 or len(like) > 0:
            conditions = "\nWHERE "
            conditions += "\n".join(where)
            if len(where) > 0 and len(like) > 0:
                conditions += ' AND '
            conditions += "\n".join(like)

        limit = '' if not limit else ' LIMIT ' + limit
        return 'DELETE FROM ' + table + conditions + limit

    def delete(self, table='', where='', limit=None, reset_data=True):
        if not table:
            if len(self._ar_from) == 0:
                if Connection.show_error:
                    raise HTTPError(500, 'Must set table name')
                return False
            table = self._ar_from[0]
        elif isinstance(table, list):
            for single_table in table:
                self.delete(table, where, limit, False)
            return
        else:
            table = self._protect_identifiers(table, True, True, False)

        if where:
            self.where(where)

        if limit:
            self.limit(limit)

        if len(self._ar_where) == 0 and len(self._ar_wherein) == 0 and len(self._ar_like) == 0:
            if Connection.show_error:
                raise HTTPError(500, 'Delete must use where')
            return False

        sql = self._delete(table, self._ar_where, self._ar_like, self._ar_limit)
        return self._query(sql)

    def empty_table(self, table=''):
        if not table:
            if len(self._ar_from) == 0:
                if Connection.show_error:
                    raise HTTPError(500, 'Must set table name')
                return False
            table = self._ar_from[0]
        else:
            table = self._protect_identifiers(table, True, True, False)

        sql = self._delete(table)
        return self._query(sql)

    def _truncate(self, table):
        return 'TRUNCATE ' + table

    def truncate(self, table=''):
        if not table:
            if len(self._ar_from) == 0:
                if Connection.show_error:
                    raise HTTPError(500, 'Must set table name')
                return False
            table = self._ar_from[0]
        else:
            table = self._protect_identifiers(table, True, True, False)

        sql = self._truncate(table)
        return self._query(sql)

class Connection:

    show_error = True
    engine = None

    @staticmethod
    def set_engine(settings):
        if not settings:
            raise HTTPError(500, 'Database configuration is required')
        Connection.engine = create_engine(
            'mysql+pymysql://' + settings['user'] + 
            ':' + settings['passwd'] + '@' +
            settings['host'] + '/' + settings['db'],
            echo=Connection.show_error,
            execution_options={
                'no_parameters' : True
            }
        )

    @staticmethod
    def create():
        try:
            return Connection.engine.connect()
        except Exception as e:
            raise HTTPError(500, 'Unable to connect to your database server using the provided settings.')

    @staticmethod
    def set_debug(val=True):
        Connection.show_error = val

class Model:
    def __init__(self, db):
        self.db = db

    def query(self):
        return Query(self.db)