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

from oslo.config import cfg
from oslo.config import fixture as config

from oslo.db import options
from tests import utils as test_utils


class DbApiOptionsTestCase(test_utils.BaseTestCase):
    def setUp(self):
        super(DbApiOptionsTestCase, self).setUp()

        config_fixture = self.useFixture(config.Config())
        self.conf = config_fixture.conf
        self.conf.register_opts(options.database_opts, group='database')
        self.config = config_fixture.config

    def test_deprecated_session_parameters(self):
        path = self.create_tempfiles([["tmp", b"""[DEFAULT]
sql_connection=x://y.z
sql_min_pool_size=10
sql_max_pool_size=20
sql_max_retries=30
sql_retry_interval=40
sql_max_overflow=50
sql_connection_debug=60
sql_connection_trace=True
"""]])[0]
        self.conf(['--config-file', path])
        self.assertEqual(self.conf.database.connection, 'x://y.z')
        self.assertEqual(self.conf.database.min_pool_size, 10)
        self.assertEqual(self.conf.database.max_pool_size, 20)
        self.assertEqual(self.conf.database.max_retries, 30)
        self.assertEqual(self.conf.database.retry_interval, 40)
        self.assertEqual(self.conf.database.max_overflow, 50)
        self.assertEqual(self.conf.database.connection_debug, 60)
        self.assertEqual(self.conf.database.connection_trace, True)

    def test_session_parameters(self):
        path = self.create_tempfiles([["tmp", b"""[database]
connection=x://y.z
min_pool_size=10
max_pool_size=20
max_retries=30
retry_interval=40
max_overflow=50
connection_debug=60
connection_trace=True
pool_timeout=7
"""]])[0]
        self.conf(['--config-file', path])
        self.assertEqual(self.conf.database.connection, 'x://y.z')
        self.assertEqual(self.conf.database.min_pool_size, 10)
        self.assertEqual(self.conf.database.max_pool_size, 20)
        self.assertEqual(self.conf.database.max_retries, 30)
        self.assertEqual(self.conf.database.retry_interval, 40)
        self.assertEqual(self.conf.database.max_overflow, 50)
        self.assertEqual(self.conf.database.connection_debug, 60)
        self.assertEqual(self.conf.database.connection_trace, True)
        self.assertEqual(self.conf.database.pool_timeout, 7)

    def test_dbapi_database_deprecated_parameters(self):
        path = self.create_tempfiles([['tmp', b'[DATABASE]\n'
                                       b'sql_connection=fake_connection\n'
                                       b'sql_idle_timeout=100\n'
                                       b'sql_min_pool_size=99\n'
                                       b'sql_max_pool_size=199\n'
                                       b'sql_max_retries=22\n'
                                       b'reconnect_interval=17\n'
                                       b'sqlalchemy_max_overflow=101\n'
                                       b'sqlalchemy_pool_timeout=5\n'
                                       ]])[0]
        self.conf(['--config-file', path])
        self.assertEqual(self.conf.database.connection, 'fake_connection')
        self.assertEqual(self.conf.database.idle_timeout, 100)
        self.assertEqual(self.conf.database.min_pool_size, 99)
        self.assertEqual(self.conf.database.max_pool_size, 199)
        self.assertEqual(self.conf.database.max_retries, 22)
        self.assertEqual(self.conf.database.retry_interval, 17)
        self.assertEqual(self.conf.database.max_overflow, 101)
        self.assertEqual(self.conf.database.pool_timeout, 5)

    def test_dbapi_database_deprecated_parameters_sql(self):
        path = self.create_tempfiles([['tmp', b'[sql]\n'
                                       b'connection=test_sql_connection\n'
                                       b'idle_timeout=99\n'
                                       ]])[0]
        self.conf(['--config-file', path])
        self.assertEqual(self.conf.database.connection, 'test_sql_connection')
        self.assertEqual(self.conf.database.idle_timeout, 99)

    def test_deprecated_dbapi_parameters(self):
        path = self.create_tempfiles([['tmp', b'[DEFAULT]\n'
                                      b'db_backend=test_123\n'
                                       ]])[0]

        self.conf(['--config-file', path])
        self.assertEqual(self.conf.database.backend, 'test_123')

    def test_dbapi_parameters(self):
        path = self.create_tempfiles([['tmp', b'[database]\n'
                                      b'backend=test_123\n'
                                       ]])[0]

        self.conf(['--config-file', path])
        self.assertEqual(self.conf.database.backend, 'test_123')

    def test_set_defaults(self):
        conf = cfg.ConfigOpts()

        options.set_defaults(conf,
                             connection='sqlite:///:memory:')

        self.assertTrue(len(conf.database.items()) > 1)
        self.assertEqual('sqlite:///:memory:', conf.database.connection)
