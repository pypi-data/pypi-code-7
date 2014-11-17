from cqlengine import connection
from djangotoolbox.db.base import FakeCursor
from cassandra.auth import PlainTextAuthProvider


class CassandraConnection(object):

    def __init__(self, **options):

        self.hosts = options.get('HOST').split(',')
        self.keyspace = options.get('NAME')
        self.user = options.get('USER')
        self.password = options.get('PASSWORD')
        self.options = options.get('OPTIONS', {})
        self.connection_options = self.options.get('connection', {})
        self.session_options = self.options.get('session', {})

        if self.user and self.password and not \
                'auth_provider' in self.connection_options:
            self.connection_options['auth_provider'] = \
                PlainTextAuthProvider(username=self.user,
                                      password=self.password)

        self.setup()

    def setup(self):
        if connection.cluster is not None:
            # already connected
            return

        connection.setup(self.hosts, self.keyspace, **self.connection_options)

        for option, value in self.session_options.iteritems():
            setattr(self.session, option, value)

    def commit(self):
        pass

    def rollback(self):
        pass

    def cursor(self):
        return FakeCursor()

    @property
    def session(self):
        return connection.get_session()

    @property
    def cluster(self):
        return connection.get_cluster()

    def execute(self, qs, *args, **kwargs):
        self.session.set_keyspace(self.keyspace)
        self.session.execute(qs, *args, **kwargs)

    def close(self):
        """ We would like to keep connection always open by default """

    def close_all(self):
        """
        Close all db connections
        """

        if self.cluster is not None:
            self.cluster.shutdown()
        if self.session is not None:
            self.session.shutdown()

        connection.cluster = None
        connection.session = None
        connection.lazy_connect_args = None
        connection.default_consistency_level = None
