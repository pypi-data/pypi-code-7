# Copyright (c) 2013 Boris Pavlovic (boris@pavlovic.me).
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import uuid

import fixtures
import mock
from oslotest import base as test_base
from oslotest import moxstubout
import six
from six.moves.urllib import parse
import sqlalchemy
from sqlalchemy.dialects import mysql
from sqlalchemy import Boolean, Index, Integer, DateTime, String, SmallInteger
from sqlalchemy import MetaData, Table, Column, ForeignKey
from sqlalchemy.engine import reflection
from sqlalchemy.engine import url as sa_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select
from sqlalchemy.types import UserDefinedType, NullType

from oslo.db import exception
from oslo.db.sqlalchemy import models
from oslo.db.sqlalchemy import provision
from oslo.db.sqlalchemy import session
from oslo.db.sqlalchemy import test_base as db_test_base
from oslo.db.sqlalchemy import utils
from tests import utils as test_utils


SA_VERSION = tuple(map(int, sqlalchemy.__version__.split('.')))


class TestSanitizeDbUrl(test_base.BaseTestCase):

    def test_url_with_cred(self):
        db_url = 'myproto://johndoe:secret@localhost/myschema'
        expected = 'myproto://****:****@localhost/myschema'
        actual = utils.sanitize_db_url(db_url)
        self.assertEqual(expected, actual)

    def test_url_with_no_cred(self):
        db_url = 'sqlite:///mysqlitefile'
        actual = utils.sanitize_db_url(db_url)
        self.assertEqual(db_url, actual)


class CustomType(UserDefinedType):
    """Dummy column type for testing unsupported types."""
    def get_col_spec(self):
        return "CustomType"


class FakeModel(object):
    def __init__(self, values):
        self.values = values

    def __getattr__(self, name):
        try:
            value = self.values[name]
        except KeyError:
            raise AttributeError(name)
        return value

    def __getitem__(self, key):
        if key in self.values:
            return self.values[key]
        else:
            raise NotImplementedError()

    def __repr__(self):
        return '<FakeModel: %s>' % self.values


class TestPaginateQuery(test_base.BaseTestCase):
    def setUp(self):
        super(TestPaginateQuery, self).setUp()
        mox_fixture = self.useFixture(moxstubout.MoxStubout())
        self.mox = mox_fixture.mox
        self.query = self.mox.CreateMockAnything()
        self.mox.StubOutWithMock(sqlalchemy, 'asc')
        self.mox.StubOutWithMock(sqlalchemy, 'desc')
        self.marker = FakeModel({
            'user_id': 'user',
            'project_id': 'p',
            'snapshot_id': 's',
        })
        self.model = FakeModel({
            'user_id': 'user',
            'project_id': 'project',
            'snapshot_id': 'snapshot',
        })

    def test_paginate_query_no_pagination_no_sort_dirs(self):
        sqlalchemy.asc('user').AndReturn('asc_3')
        self.query.order_by('asc_3').AndReturn(self.query)
        sqlalchemy.asc('project').AndReturn('asc_2')
        self.query.order_by('asc_2').AndReturn(self.query)
        sqlalchemy.asc('snapshot').AndReturn('asc_1')
        self.query.order_by('asc_1').AndReturn(self.query)
        self.query.limit(5).AndReturn(self.query)
        self.mox.ReplayAll()
        utils.paginate_query(self.query, self.model, 5,
                             ['user_id', 'project_id', 'snapshot_id'])

    def test_paginate_query_no_pagination(self):
        sqlalchemy.asc('user').AndReturn('asc')
        self.query.order_by('asc').AndReturn(self.query)
        sqlalchemy.desc('project').AndReturn('desc')
        self.query.order_by('desc').AndReturn(self.query)
        self.query.limit(5).AndReturn(self.query)
        self.mox.ReplayAll()
        utils.paginate_query(self.query, self.model, 5,
                             ['user_id', 'project_id'],
                             sort_dirs=['asc', 'desc'])

    def test_paginate_query_attribute_error(self):
        sqlalchemy.asc('user').AndReturn('asc')
        self.query.order_by('asc').AndReturn(self.query)
        self.mox.ReplayAll()
        self.assertRaises(exception.InvalidSortKey,
                          utils.paginate_query, self.query,
                          self.model, 5, ['user_id', 'non-existent key'])

    def test_paginate_query_assertion_error(self):
        self.mox.ReplayAll()
        self.assertRaises(AssertionError,
                          utils.paginate_query, self.query,
                          self.model, 5, ['user_id'],
                          marker=self.marker,
                          sort_dir='asc', sort_dirs=['asc'])

    def test_paginate_query_assertion_error_2(self):
        self.mox.ReplayAll()
        self.assertRaises(AssertionError,
                          utils.paginate_query, self.query,
                          self.model, 5, ['user_id'],
                          marker=self.marker,
                          sort_dir=None, sort_dirs=['asc', 'desk'])

    def test_paginate_query(self):
        sqlalchemy.asc('user').AndReturn('asc_1')
        self.query.order_by('asc_1').AndReturn(self.query)
        sqlalchemy.desc('project').AndReturn('desc_1')
        self.query.order_by('desc_1').AndReturn(self.query)
        self.mox.StubOutWithMock(sqlalchemy.sql, 'and_')
        sqlalchemy.sql.and_(False).AndReturn('some_crit')
        sqlalchemy.sql.and_(True, False).AndReturn('another_crit')
        self.mox.StubOutWithMock(sqlalchemy.sql, 'or_')
        sqlalchemy.sql.or_('some_crit', 'another_crit').AndReturn('some_f')
        self.query.filter('some_f').AndReturn(self.query)
        self.query.limit(5).AndReturn(self.query)
        self.mox.ReplayAll()
        utils.paginate_query(self.query, self.model, 5,
                             ['user_id', 'project_id'],
                             marker=self.marker,
                             sort_dirs=['asc', 'desc'])

    def test_paginate_query_value_error(self):
        sqlalchemy.asc('user').AndReturn('asc_1')
        self.query.order_by('asc_1').AndReturn(self.query)
        self.mox.ReplayAll()
        self.assertRaises(ValueError, utils.paginate_query,
                          self.query, self.model, 5, ['user_id', 'project_id'],
                          marker=self.marker, sort_dirs=['asc', 'mixed'])


class TestMigrationUtils(db_test_base.DbTestCase):

    """Class for testing utils that are used in db migrations."""

    def setUp(self):
        super(TestMigrationUtils, self).setUp()
        self.meta = MetaData(bind=self.engine)
        self.conn = self.engine.connect()
        self.addCleanup(self.meta.drop_all)
        self.addCleanup(self.conn.close)

    def _populate_db_for_drop_duplicate_entries(self, engine, meta,
                                                table_name):
        values = [
            {'id': 11, 'a': 3, 'b': 10, 'c': 'abcdef'},
            {'id': 12, 'a': 5, 'b': 10, 'c': 'abcdef'},
            {'id': 13, 'a': 6, 'b': 10, 'c': 'abcdef'},
            {'id': 14, 'a': 7, 'b': 10, 'c': 'abcdef'},
            {'id': 21, 'a': 1, 'b': 20, 'c': 'aa'},
            {'id': 31, 'a': 1, 'b': 20, 'c': 'bb'},
            {'id': 41, 'a': 1, 'b': 30, 'c': 'aef'},
            {'id': 42, 'a': 2, 'b': 30, 'c': 'aef'},
            {'id': 43, 'a': 3, 'b': 30, 'c': 'aef'}
        ]

        test_table = Table(table_name, meta,
                           Column('id', Integer, primary_key=True,
                                  nullable=False),
                           Column('a', Integer),
                           Column('b', Integer),
                           Column('c', String(255)),
                           Column('deleted', Integer, default=0),
                           Column('deleted_at', DateTime),
                           Column('updated_at', DateTime))

        test_table.create()
        engine.execute(test_table.insert(), values)
        return test_table, values

    def test_drop_old_duplicate_entries_from_table(self):
        table_name = "__test_tmp_table__"

        test_table, values = self._populate_db_for_drop_duplicate_entries(
            self.engine, self.meta, table_name)
        utils.drop_old_duplicate_entries_from_table(
            self.engine, table_name, False, 'b', 'c')

        uniq_values = set()
        expected_ids = []
        for value in sorted(values, key=lambda x: x['id'], reverse=True):
            uniq_value = (('b', value['b']), ('c', value['c']))
            if uniq_value in uniq_values:
                continue
            uniq_values.add(uniq_value)
            expected_ids.append(value['id'])

        real_ids = [row[0] for row in
                    self.engine.execute(select([test_table.c.id])).fetchall()]

        self.assertEqual(len(real_ids), len(expected_ids))
        for id_ in expected_ids:
            self.assertTrue(id_ in real_ids)

    def test_drop_dup_entries_in_file_conn(self):
        table_name = "__test_tmp_table__"
        tmp_db_file = self.create_tempfiles([['name', '']], ext='.sql')[0]
        in_file_engine = session.EngineFacade(
            'sqlite:///%s' % tmp_db_file).get_engine()
        meta = MetaData()
        meta.bind = in_file_engine
        test_table, values = self._populate_db_for_drop_duplicate_entries(
            in_file_engine, meta, table_name)
        utils.drop_old_duplicate_entries_from_table(
            in_file_engine, table_name, False, 'b', 'c')

    def test_drop_old_duplicate_entries_from_table_soft_delete(self):
        table_name = "__test_tmp_table__"

        table, values = self._populate_db_for_drop_duplicate_entries(
            self.engine, self.meta, table_name)
        utils.drop_old_duplicate_entries_from_table(self.engine, table_name,
                                                    True, 'b', 'c')
        uniq_values = set()
        expected_values = []
        soft_deleted_values = []

        for value in sorted(values, key=lambda x: x['id'], reverse=True):
            uniq_value = (('b', value['b']), ('c', value['c']))
            if uniq_value in uniq_values:
                soft_deleted_values.append(value)
                continue
            uniq_values.add(uniq_value)
            expected_values.append(value)

        base_select = table.select()

        rows_select = base_select.where(table.c.deleted != table.c.id)
        row_ids = [row['id'] for row in
                   self.engine.execute(rows_select).fetchall()]
        self.assertEqual(len(row_ids), len(expected_values))
        for value in expected_values:
            self.assertTrue(value['id'] in row_ids)

        deleted_rows_select = base_select.where(
            table.c.deleted == table.c.id)
        deleted_rows_ids = [row['id'] for row in
                            self.engine.execute(
                                deleted_rows_select).fetchall()]
        self.assertEqual(len(deleted_rows_ids),
                         len(values) - len(row_ids))
        for value in soft_deleted_values:
            self.assertTrue(value['id'] in deleted_rows_ids)

    def test_change_deleted_column_type_does_not_drop_index(self):
        table_name = 'abc'

        indexes = {
            'idx_a_deleted': ['a', 'deleted'],
            'idx_b_deleted': ['b', 'deleted'],
            'idx_a': ['a']
        }

        index_instances = [Index(name, *columns)
                           for name, columns in six.iteritems(indexes)]

        table = Table(table_name, self.meta,
                      Column('id', Integer, primary_key=True),
                      Column('a', String(255)),
                      Column('b', String(255)),
                      Column('deleted', Boolean),
                      *index_instances)
        table.create()
        utils.change_deleted_column_type_to_id_type(self.engine, table_name)
        utils.change_deleted_column_type_to_boolean(self.engine, table_name)

        insp = reflection.Inspector.from_engine(self.engine)
        real_indexes = insp.get_indexes(table_name)
        self.assertEqual(len(real_indexes), 3)
        for index in real_indexes:
            name = index['name']
            self.assertIn(name, indexes)
            self.assertEqual(set(index['column_names']),
                             set(indexes[name]))

    def test_change_deleted_column_type_to_id_type_integer(self):
        table_name = 'abc'
        table = Table(table_name, self.meta,
                      Column('id', Integer, primary_key=True),
                      Column('deleted', Boolean))
        table.create()
        utils.change_deleted_column_type_to_id_type(self.engine, table_name)

        table = utils.get_table(self.engine, table_name)
        self.assertTrue(isinstance(table.c.deleted.type, Integer))

    def test_change_deleted_column_type_to_id_type_string(self):
        table_name = 'abc'
        table = Table(table_name, self.meta,
                      Column('id', String(255), primary_key=True),
                      Column('deleted', Boolean))
        table.create()
        utils.change_deleted_column_type_to_id_type(self.engine, table_name)

        table = utils.get_table(self.engine, table_name)
        self.assertTrue(isinstance(table.c.deleted.type, String))

    @db_test_base.backend_specific('sqlite')
    def test_change_deleted_column_type_to_id_type_custom(self):
        table_name = 'abc'
        table = Table(table_name, self.meta,
                      Column('id', Integer, primary_key=True),
                      Column('foo', CustomType),
                      Column('deleted', Boolean))
        table.create()

        # reflection of custom types has been fixed upstream
        if SA_VERSION < (0, 9, 0):
            self.assertRaises(exception.ColumnError,
                              utils.change_deleted_column_type_to_id_type,
                              self.engine, table_name)

        fooColumn = Column('foo', CustomType())
        utils.change_deleted_column_type_to_id_type(self.engine, table_name,
                                                    foo=fooColumn)

        table = utils.get_table(self.engine, table_name)
        # NOTE(boris-42): There is no way to check has foo type CustomType.
        #                 but sqlalchemy will set it to NullType. This has
        #                 been fixed upstream in recent SA versions
        if SA_VERSION < (0, 9, 0):
            self.assertTrue(isinstance(table.c.foo.type, NullType))
        self.assertTrue(isinstance(table.c.deleted.type, Integer))

    def test_change_deleted_column_type_to_boolean(self):
        expected_types = {'mysql': mysql.TINYINT,
                          'ibm_db_sa': SmallInteger}
        table_name = 'abc'
        table = Table(table_name, self.meta,
                      Column('id', Integer, primary_key=True),
                      Column('deleted', Integer))
        table.create()

        utils.change_deleted_column_type_to_boolean(self.engine, table_name)

        table = utils.get_table(self.engine, table_name)
        self.assertIsInstance(table.c.deleted.type,
                              expected_types.get(self.engine.name, Boolean))

    def test_change_deleted_column_type_to_boolean_with_fc(self):
        expected_types = {'mysql': mysql.TINYINT,
                          'ibm_db_sa': SmallInteger}
        table_name_1 = 'abc'
        table_name_2 = 'bcd'

        table_1 = Table(table_name_1, self.meta,
                        Column('id', Integer, primary_key=True),
                        Column('deleted', Integer))
        table_1.create()

        table_2 = Table(table_name_2, self.meta,
                        Column('id', Integer, primary_key=True),
                        Column('foreign_id', Integer,
                               ForeignKey('%s.id' % table_name_1)),
                        Column('deleted', Integer))
        table_2.create()

        utils.change_deleted_column_type_to_boolean(self.engine, table_name_2)

        table = utils.get_table(self.engine, table_name_2)
        self.assertIsInstance(table.c.deleted.type,
                              expected_types.get(self.engine.name, Boolean))

    @db_test_base.backend_specific('sqlite')
    def test_change_deleted_column_type_to_boolean_type_custom(self):
        table_name = 'abc'
        table = Table(table_name, self.meta,
                      Column('id', Integer, primary_key=True),
                      Column('foo', CustomType),
                      Column('deleted', Integer))
        table.create()

        # reflection of custom types has been fixed upstream
        if SA_VERSION < (0, 9, 0):
            self.assertRaises(exception.ColumnError,
                              utils.change_deleted_column_type_to_boolean,
                              self.engine, table_name)

        fooColumn = Column('foo', CustomType())
        utils.change_deleted_column_type_to_boolean(self.engine, table_name,
                                                    foo=fooColumn)

        table = utils.get_table(self.engine, table_name)
        # NOTE(boris-42): There is no way to check has foo type CustomType.
        #                 but sqlalchemy will set it to NullType. This has
        #                 been fixed upstream in recent SA versions
        if SA_VERSION < (0, 9, 0):
            self.assertTrue(isinstance(table.c.foo.type, NullType))
        self.assertTrue(isinstance(table.c.deleted.type, Boolean))

    @db_test_base.backend_specific('sqlite')
    def test_change_deleted_column_type_sqlite_drops_check_constraint(self):
        table_name = 'abc'
        table = Table(table_name, self.meta,
                      Column('id', Integer, primary_key=True),
                      Column('deleted', Boolean))
        table.create()

        utils._change_deleted_column_type_to_id_type_sqlite(self.engine,
                                                            table_name)
        table = Table(table_name, self.meta, autoload=True)
        # NOTE(I159): if the CHECK constraint has been dropped (expected
        # behavior), any integer value can be inserted, otherwise only 1 or 0.
        self.engine.execute(table.insert({'deleted': 10}))

    def test_insert_from_select(self):
        insert_table_name = "__test_insert_to_table__"
        select_table_name = "__test_select_from_table__"
        uuidstrs = []
        for unused in range(10):
            uuidstrs.append(uuid.uuid4().hex)
        insert_table = Table(
            insert_table_name, self.meta,
            Column('id', Integer, primary_key=True,
                   nullable=False, autoincrement=True),
            Column('uuid', String(36), nullable=False))
        select_table = Table(
            select_table_name, self.meta,
            Column('id', Integer, primary_key=True,
                   nullable=False, autoincrement=True),
            Column('uuid', String(36), nullable=False))

        insert_table.create()
        select_table.create()
        # Add 10 rows to select_table
        for uuidstr in uuidstrs:
            ins_stmt = select_table.insert().values(uuid=uuidstr)
            self.conn.execute(ins_stmt)

        # Select 4 rows in one chunk from select_table
        column = select_table.c.id
        query_insert = select([select_table],
                              select_table.c.id < 5).order_by(column)
        insert_statement = utils.InsertFromSelect(insert_table,
                                                  query_insert)
        result_insert = self.conn.execute(insert_statement)
        # Verify we insert 4 rows
        self.assertEqual(result_insert.rowcount, 4)

        query_all = select([insert_table]).where(
            insert_table.c.uuid.in_(uuidstrs))
        rows = self.conn.execute(query_all).fetchall()
        # Verify we really have 4 rows in insert_table
        self.assertEqual(len(rows), 4)


class PostgesqlTestMigrations(TestMigrationUtils,
                              db_test_base.PostgreSQLOpportunisticTestCase):

    """Test migrations on PostgreSQL."""
    pass


class MySQLTestMigrations(TestMigrationUtils,
                          db_test_base.MySQLOpportunisticTestCase):

    """Test migrations on MySQL."""
    pass


class TestConnectionUtils(test_utils.BaseTestCase):

    def setUp(self):
        super(TestConnectionUtils, self).setUp()

        self.full_credentials = {'backend': 'mysql',
                                 'database': 'test',
                                 'user': 'dude',
                                 'passwd': 'pass'}

        self.connect_string = 'mysql://dude:pass@localhost/test'

    def test_connect_string(self):
        connect_string = utils.get_connect_string(**self.full_credentials)
        self.assertEqual(connect_string, self.connect_string)

    def test_connect_string_sqlite(self):
        sqlite_credentials = {'backend': 'sqlite', 'database': 'test.db'}
        connect_string = utils.get_connect_string(**sqlite_credentials)
        self.assertEqual(connect_string, 'sqlite:///test.db')

    def test_is_backend_avail(self):
        self.mox.StubOutWithMock(sqlalchemy.engine.base.Engine, 'connect')
        fake_connection = self.mox.CreateMockAnything()
        fake_connection.close()
        sqlalchemy.engine.base.Engine.connect().AndReturn(fake_connection)
        self.mox.ReplayAll()

        self.assertTrue(utils.is_backend_avail(**self.full_credentials))

    def test_is_backend_unavail(self):
        log = self.useFixture(fixtures.FakeLogger())
        err = OperationalError("Can't connect to database", None, None)
        error_msg = "The mysql backend is unavailable: %s\n" % err
        self.mox.StubOutWithMock(sqlalchemy.engine.base.Engine, 'connect')
        sqlalchemy.engine.base.Engine.connect().AndRaise(err)
        self.mox.ReplayAll()
        self.assertFalse(utils.is_backend_avail(**self.full_credentials))
        self.assertEqual(error_msg, log.output)

    def test_ensure_backend_available(self):
        self.mox.StubOutWithMock(sqlalchemy.engine.base.Engine, 'connect')
        fake_connection = self.mox.CreateMockAnything()
        fake_connection.close()
        sqlalchemy.engine.base.Engine.connect().AndReturn(fake_connection)
        self.mox.ReplayAll()

        eng = provision.Backend._ensure_backend_available(self.connect_string)
        self.assertIsInstance(eng, sqlalchemy.engine.base.Engine)
        self.assertEqual(self.connect_string, str(eng.url))

    def test_ensure_backend_available_no_connection_raises(self):
        log = self.useFixture(fixtures.FakeLogger())
        err = OperationalError("Can't connect to database", None, None)
        self.mox.StubOutWithMock(sqlalchemy.engine.base.Engine, 'connect')
        sqlalchemy.engine.base.Engine.connect().AndRaise(err)
        self.mox.ReplayAll()

        exc = self.assertRaises(
            exception.BackendNotAvailable,
            provision.Backend._ensure_backend_available, self.connect_string
        )
        self.assertEqual("Could not connect", str(exc))
        self.assertEqual(
            "The mysql backend is unavailable: %s" % err,
            log.output.strip())

    def test_ensure_backend_available_no_dbapi_raises(self):
        log = self.useFixture(fixtures.FakeLogger())
        self.mox.StubOutWithMock(sqlalchemy, 'create_engine')
        sqlalchemy.create_engine(
            sa_url.make_url(self.connect_string)).AndRaise(
            ImportError("Can't import DBAPI module foobar"))
        self.mox.ReplayAll()

        exc = self.assertRaises(
            exception.BackendNotAvailable,
            provision.Backend._ensure_backend_available, self.connect_string
        )
        self.assertEqual("No DBAPI installed", str(exc))
        self.assertEqual(
            "The mysql backend is unavailable: Can't import "
            "DBAPI module foobar", log.output.strip())

    def test_get_db_connection_info(self):
        conn_pieces = parse.urlparse(self.connect_string)
        self.assertEqual(utils.get_db_connection_info(conn_pieces),
                         ('dude', 'pass', 'test', 'localhost'))

    def test_connect_string_host(self):
        self.full_credentials['host'] = 'myhost'
        connect_string = utils.get_connect_string(**self.full_credentials)
        self.assertEqual(connect_string, 'mysql://dude:pass@myhost/test')


class MyModelSoftDeletedProjectId(declarative_base(), models.ModelBase,
                                  models.SoftDeleteMixin):
    __tablename__ = 'soft_deleted_project_id_test_model'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)


class MyModel(declarative_base(), models.ModelBase):
    __tablename__ = 'test_model'
    id = Column(Integer, primary_key=True)


class MyModelSoftDeleted(declarative_base(), models.ModelBase,
                         models.SoftDeleteMixin):
    __tablename__ = 'soft_deleted_test_model'
    id = Column(Integer, primary_key=True)


class TestModelQuery(test_base.BaseTestCase):

    def setUp(self):
        super(TestModelQuery, self).setUp()

        self.session = mock.MagicMock()
        self.session.query.return_value = self.session.query
        self.session.query.filter.return_value = self.session.query

    def test_wrong_model(self):
        self.assertRaises(TypeError, utils.model_query,
                          FakeModel, session=self.session)

    def test_no_soft_deleted(self):
        self.assertRaises(ValueError, utils.model_query,
                          MyModel, session=self.session, deleted=True)

    def test_deleted_false(self):
        mock_query = utils.model_query(
            MyModelSoftDeleted, session=self.session, deleted=False)

        deleted_filter = mock_query.filter.call_args[0][0]
        self.assertEqual(str(deleted_filter),
                         'soft_deleted_test_model.deleted = :deleted_1')
        self.assertEqual(deleted_filter.right.value,
                         MyModelSoftDeleted.__mapper__.c.deleted.default.arg)

    def test_deleted_true(self):
        mock_query = utils.model_query(
            MyModelSoftDeleted, session=self.session, deleted=True)

        deleted_filter = mock_query.filter.call_args[0][0]
        self.assertEqual(str(deleted_filter),
                         'soft_deleted_test_model.deleted != :deleted_1')
        self.assertEqual(deleted_filter.right.value,
                         MyModelSoftDeleted.__mapper__.c.deleted.default.arg)

    @mock.patch.object(utils, "_read_deleted_filter")
    def test_no_deleted_value(self, _read_deleted_filter):
        utils.model_query(MyModelSoftDeleted, session=self.session)
        self.assertEqual(_read_deleted_filter.call_count, 0)

    def test_project_filter(self):
        project_id = 10

        mock_query = utils.model_query(
            MyModelSoftDeletedProjectId, session=self.session,
            project_only=True, project_id=project_id)

        deleted_filter = mock_query.filter.call_args[0][0]
        self.assertEqual(
            str(deleted_filter),
            'soft_deleted_project_id_test_model.project_id = :project_id_1')
        self.assertEqual(deleted_filter.right.value, project_id)

    def test_project_filter_wrong_model(self):
        self.assertRaises(ValueError, utils.model_query,
                          MyModelSoftDeleted, session=self.session,
                          project_id=10)

    def test_project_filter_allow_none(self):
        mock_query = utils.model_query(
            MyModelSoftDeletedProjectId,
            session=self.session, project_id=(10, None))

        self.assertEqual(
            str(mock_query.filter.call_args[0][0]),
            'soft_deleted_project_id_test_model.project_id'
            ' IN (:project_id_1, NULL)'
        )

    def test_model_query_common(self):
        utils.model_query(MyModel, args=(MyModel.id,), session=self.session)
        self.session.query.assert_called_with(MyModel.id)


class TestUtils(db_test_base.DbTestCase):
    def setUp(self):
        super(TestUtils, self).setUp()
        meta = MetaData(bind=self.engine)
        self.test_table = Table(
            'test_table',
            meta,
            Column('a', Integer),
            Column('b', Integer)
        )
        self.test_table.create()
        self.addCleanup(meta.drop_all)

    def test_index_exists(self):
        self.assertFalse(utils.index_exists(self.engine, 'test_table',
                                            'new_index'))
        Index('new_index', self.test_table.c.a).create(self.engine)
        self.assertTrue(utils.index_exists(self.engine, 'test_table',
                                           'new_index'))

    def test_add_index(self):
        self.assertFalse(utils.index_exists(self.engine, 'test_table',
                                            'new_index'))
        utils.add_index(self.engine, 'test_table', 'new_index', ('a',))
        self.assertTrue(utils.index_exists(self.engine, 'test_table',
                                           'new_index'))

    def test_add_existing_index(self):
        Index('new_index', self.test_table.c.a).create(self.engine)
        self.assertRaises(ValueError, utils.add_index, self.engine,
                          'test_table', 'new_index', ('a',))

    def test_drop_index(self):
        Index('new_index', self.test_table.c.a).create(self.engine)
        utils.drop_index(self.engine, 'test_table', 'new_index')
        self.assertFalse(utils.index_exists(self.engine, 'test_table',
                         'new_index'))

    def test_drop_unexisting_index(self):
        self.assertRaises(ValueError, utils.drop_index, self.engine,
                          'test_table', 'new_index')

    @mock.patch('oslo.db.sqlalchemy.utils.drop_index')
    @mock.patch('oslo.db.sqlalchemy.utils.add_index')
    def test_change_index_columns(self, add_index, drop_index):
        utils.change_index_columns(self.engine, 'test_table', 'a_index',
                                   ('a',))
        utils.drop_index.assert_called_once_with(self.engine, 'test_table',
                                                 'a_index')
        utils.add_index.assert_called_once_with(self.engine, 'test_table',
                                                'a_index', ('a',))

    def test_column_exists(self):
        for col in ['a', 'b']:
            self.assertTrue(utils.column_exists(self.engine, 'test_table',
                                                col))
        self.assertFalse(utils.column_exists(self.engine, 'test_table',
                                             'fake_column'))


class TestUtilsMysqlOpportunistically(
        TestUtils, db_test_base.MySQLOpportunisticTestCase):
    pass


class TestUtilsPostgresqlOpportunistically(
        TestUtils, db_test_base.PostgreSQLOpportunisticTestCase):
    pass


class TestDialectFunctionDispatcher(test_base.BaseTestCase):
    def _single_fixture(self):
        callable_fn = mock.Mock()

        dispatcher = orig = utils.dispatch_for_dialect("*")(
            callable_fn.default)
        dispatcher = dispatcher.dispatch_for("sqlite")(callable_fn.sqlite)
        dispatcher = dispatcher.dispatch_for("mysql+mysqldb")(
            callable_fn.mysql_mysqldb)
        dispatcher = dispatcher.dispatch_for("postgresql")(
            callable_fn.postgresql)

        self.assertTrue(dispatcher is orig)

        return dispatcher, callable_fn

    def _multiple_fixture(self):
        callable_fn = mock.Mock()

        for targ in [
            callable_fn.default,
            callable_fn.sqlite,
            callable_fn.mysql_mysqldb,
            callable_fn.postgresql,
            callable_fn.postgresql_psycopg2,
            callable_fn.pyodbc
        ]:
            targ.return_value = None

        dispatcher = orig = utils.dispatch_for_dialect("*", multiple=True)(
            callable_fn.default)
        dispatcher = dispatcher.dispatch_for("sqlite")(callable_fn.sqlite)
        dispatcher = dispatcher.dispatch_for("mysql+mysqldb")(
            callable_fn.mysql_mysqldb)
        dispatcher = dispatcher.dispatch_for("postgresql+*")(
            callable_fn.postgresql)
        dispatcher = dispatcher.dispatch_for("postgresql+psycopg2")(
            callable_fn.postgresql_psycopg2)
        dispatcher = dispatcher.dispatch_for("*+pyodbc")(
            callable_fn.pyodbc)

        self.assertTrue(dispatcher is orig)

        return dispatcher, callable_fn

    def test_single(self):

        dispatcher, callable_fn = self._single_fixture()
        dispatcher("sqlite://", 1)
        dispatcher("postgresql+psycopg2://u:p@h/t", 2)
        dispatcher("mysql://u:p@h/t", 3)
        dispatcher("mysql+mysqlconnector://u:p@h/t", 4)

        self.assertEqual(
            [
                mock.call.sqlite('sqlite://', 1),
                mock.call.postgresql("postgresql+psycopg2://u:p@h/t", 2),
                mock.call.mysql_mysqldb("mysql://u:p@h/t", 3),
                mock.call.default("mysql+mysqlconnector://u:p@h/t", 4)
            ],
            callable_fn.mock_calls)

    def test_single_kwarg(self):
        dispatcher, callable_fn = self._single_fixture()
        dispatcher("sqlite://", foo='bar')
        dispatcher("postgresql+psycopg2://u:p@h/t", 1, x='y')

        self.assertEqual(
            [
                mock.call.sqlite('sqlite://', foo='bar'),
                mock.call.postgresql(
                    "postgresql+psycopg2://u:p@h/t",
                    1, x='y'),
            ],
            callable_fn.mock_calls)

    def test_dispatch_on_target(self):
        callable_fn = mock.Mock()

        @utils.dispatch_for_dialect("*")
        def default_fn(url, x, y):
            callable_fn.default(url, x, y)

        @default_fn.dispatch_for("sqlite")
        def sqlite_fn(url, x, y):
            callable_fn.sqlite(url, x, y)
            default_fn.dispatch_on_drivername("*")(url, x, y)

        default_fn("sqlite://", 4, 5)
        self.assertEqual(
            [
                mock.call.sqlite("sqlite://", 4, 5),
                mock.call.default("sqlite://", 4, 5)
            ],
            callable_fn.mock_calls
        )

    def test_single_no_dispatcher(self):
        callable_fn = mock.Mock()

        dispatcher = utils.dispatch_for_dialect("sqlite")(callable_fn.sqlite)
        dispatcher = dispatcher.dispatch_for("mysql")(callable_fn.mysql)
        exc = self.assertRaises(
            ValueError,
            dispatcher, "postgresql://s:t@localhost/test"
        )
        self.assertEqual(
            "No default function found for driver: 'postgresql+psycopg2'",
            str(exc)
        )

    def test_multiple_no_dispatcher(self):
        callable_fn = mock.Mock()

        dispatcher = utils.dispatch_for_dialect("sqlite", multiple=True)(
            callable_fn.sqlite)
        dispatcher = dispatcher.dispatch_for("mysql")(callable_fn.mysql)
        dispatcher("postgresql://s:t@localhost/test")
        self.assertEqual(
            [], callable_fn.mock_calls
        )

    def test_multiple_no_driver(self):
        callable_fn = mock.Mock(
            default=mock.Mock(return_value=None),
            sqlite=mock.Mock(return_value=None)
        )

        dispatcher = utils.dispatch_for_dialect("*", multiple=True)(
            callable_fn.default)
        dispatcher = dispatcher.dispatch_for("sqlite")(
            callable_fn.sqlite)

        dispatcher.dispatch_on_drivername("sqlite")("foo")
        self.assertEqual(
            [mock.call.sqlite("foo"), mock.call.default("foo")],
            callable_fn.mock_calls
        )

    def test_multiple_nesting(self):
        callable_fn = mock.Mock(
            default=mock.Mock(return_value=None),
            mysql=mock.Mock(return_value=None)
        )

        dispatcher = utils.dispatch_for_dialect("*", multiple=True)(
            callable_fn.default)

        dispatcher = dispatcher.dispatch_for("mysql+mysqlconnector")(
            dispatcher.dispatch_for("mysql+mysqldb")(
                callable_fn.mysql
            )
        )

        mysqldb_url = sqlalchemy.engine.url.make_url("mysql+mysqldb://")
        mysqlconnector_url = sqlalchemy.engine.url.make_url(
            "mysql+mysqlconnector://")
        sqlite_url = sqlalchemy.engine.url.make_url("sqlite://")

        dispatcher(mysqldb_url, 1)
        dispatcher(mysqlconnector_url, 2)
        dispatcher(sqlite_url, 3)

        self.assertEqual(
            [
                mock.call.mysql(mysqldb_url, 1),
                mock.call.default(mysqldb_url, 1),
                mock.call.mysql(mysqlconnector_url, 2),
                mock.call.default(mysqlconnector_url, 2),
                mock.call.default(sqlite_url, 3)
            ],
            callable_fn.mock_calls
        )

    def test_single_retval(self):
        dispatcher, callable_fn = self._single_fixture()
        callable_fn.mysql_mysqldb.return_value = 5

        self.assertEqual(
            dispatcher("mysql://u:p@h/t", 3), 5
        )

    def test_engine(self):
        eng = sqlalchemy.create_engine("sqlite:///path/to/my/db.db")
        dispatcher, callable_fn = self._single_fixture()

        dispatcher(eng)
        self.assertEqual(
            [mock.call.sqlite(eng)],
            callable_fn.mock_calls
        )

    def test_url(self):
        url = sqlalchemy.engine.url.make_url(
            "mysql+mysqldb://scott:tiger@localhost/test")
        dispatcher, callable_fn = self._single_fixture()

        dispatcher(url, 15)
        self.assertEqual(
            [mock.call.mysql_mysqldb(url, 15)],
            callable_fn.mock_calls
        )

    def test_invalid_target(self):
        dispatcher, callable_fn = self._single_fixture()

        exc = self.assertRaises(
            ValueError,
            dispatcher, 20
        )
        self.assertEqual("Invalid target type: 20", str(exc))

    def test_invalid_dispatch(self):
        callable_fn = mock.Mock()

        dispatcher = utils.dispatch_for_dialect("*")(callable_fn.default)

        exc = self.assertRaises(
            ValueError,
            dispatcher.dispatch_for("+pyodbc"), callable_fn.pyodbc
        )
        self.assertEqual(
            "Couldn't parse database[+driver]: '+pyodbc'",
            str(exc)
        )

    def test_single_only_one_target(self):
        callable_fn = mock.Mock()

        dispatcher = utils.dispatch_for_dialect("*")(callable_fn.default)
        dispatcher = dispatcher.dispatch_for("sqlite")(callable_fn.sqlite)

        exc = self.assertRaises(
            TypeError,
            dispatcher.dispatch_for("sqlite"), callable_fn.sqlite2
        )
        self.assertEqual(
            "Multiple functions for expression 'sqlite'", str(exc)
        )

    def test_multiple(self):
        dispatcher, callable_fn = self._multiple_fixture()

        dispatcher("postgresql+pyodbc://", 1)
        dispatcher("mysql://", 2)
        dispatcher("ibm_db_sa+db2://", 3)
        dispatcher("postgresql+psycopg2://", 4)

        # TODO(zzzeek): there is a deterministic order here, but we might
        # want to tweak it, or maybe provide options.  default first?
        # most specific first?  is *+pyodbc or postgresql+* more specific?
        self.assertEqual(
            [
                mock.call.postgresql('postgresql+pyodbc://', 1),
                mock.call.pyodbc('postgresql+pyodbc://', 1),
                mock.call.default('postgresql+pyodbc://', 1),
                mock.call.mysql_mysqldb('mysql://', 2),
                mock.call.default('mysql://', 2),
                mock.call.default('ibm_db_sa+db2://', 3),
                mock.call.postgresql_psycopg2('postgresql+psycopg2://', 4),
                mock.call.postgresql('postgresql+psycopg2://', 4),
                mock.call.default('postgresql+psycopg2://', 4),
            ],
            callable_fn.mock_calls
        )

    def test_multiple_no_return_value(self):
        dispatcher, callable_fn = self._multiple_fixture()
        callable_fn.sqlite.return_value = 5

        exc = self.assertRaises(
            TypeError,
            dispatcher, "sqlite://"
        )
        self.assertEqual(
            "Return value not allowed for multiple filtered function",
            str(exc)
        )


class TestGetInnoDBTables(db_test_base.MySQLOpportunisticTestCase):

    def test_all_tables_use_innodb(self):
        self.engine.execute("CREATE TABLE customers "
                            "(a INT, b CHAR (20), INDEX (a)) ENGINE=InnoDB")
        self.assertEqual([], utils.get_non_innodb_tables(self.engine))

    def test_all_tables_use_innodb_false(self):
        self.engine.execute("CREATE TABLE employee "
                            "(i INT) ENGINE=MEMORY")
        self.assertEqual(['employee'],
                         utils.get_non_innodb_tables(self.engine))

    def test_skip_tables_use_default_value(self):
        self.engine.execute("CREATE TABLE migrate_version "
                            "(i INT) ENGINE=MEMORY")
        self.assertEqual([],
                         utils.get_non_innodb_tables(self.engine))

    def test_skip_tables_use_passed_value(self):
        self.engine.execute("CREATE TABLE some_table "
                            "(i INT) ENGINE=MEMORY")
        self.assertEqual([],
                         utils.get_non_innodb_tables(
                             self.engine, skip_tables=('some_table',)))

    def test_skip_tables_use_empty_list(self):
        self.engine.execute("CREATE TABLE some_table_3 "
                            "(i INT) ENGINE=MEMORY")
        self.assertEqual(['some_table_3'],
                         utils.get_non_innodb_tables(
                         self.engine, skip_tables=()))

    def test_skip_tables_use_several_values(self):
        self.engine.execute("CREATE TABLE some_table_1 "
                            "(i INT) ENGINE=MEMORY")
        self.engine.execute("CREATE TABLE some_table_2 "
                            "(i INT) ENGINE=MEMORY")
        self.assertEqual([],
                         utils.get_non_innodb_tables(
                             self.engine,
                             skip_tables=('some_table_1', 'some_table_2')))
