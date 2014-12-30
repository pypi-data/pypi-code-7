import getpass

from sqlalchemy import sessionmaker


class TestDatabaseCreator(object):
    """Responsible for creating and destroying the Fulcrum test database."""

    def __init__(self, engine):
        """Initialize a new TestDatabaseCreator instance.

        Args:
            engine (sqlalchemy.Engine): engine used to connect to the database
                server.
        """
        self._engine = engine.execution_options(isolation_level="AUTOCOMMIT")
        self._session = sessionmaker(bind=self._engine, autocommit=True)()

    def _get_test_db_name(self, name=None):
        return "test_fulcrum_{0}".format(name or getpass.getuser())

    def drop_test_database(self, name=None):
        """Drops the test database if it exists."""
        # This is an SQL injection vulnerability, but we assume this is only
        # executed in our disposable and thus safe testing environments (TODO).
        self._engine.execute("DROP DATABASE IF EXISTS {0}".format(
            self._get_test_db_name(name=name)))

    def create_test_database(self, name=None):
        """Creates the test database."""
        self.drop_test_database(name=name)
        self._engine.execute("CREATE DATABASE {0}"\
            .format(self._get_test_db_name(name=name)))
