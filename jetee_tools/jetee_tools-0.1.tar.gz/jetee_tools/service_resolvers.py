import DNS


class JeteeServiceConfigResolver(object):
    dns_server = '172.17.42.1'
    service_ip = u'172.17.42.1'
    protocol = u''
    port = None

    def get_real_host(self):
        return u'{}.service.consul'.format(self.host)

    def __init__(self, host):
        self.host = host
        self.resolve_port()

    def render(self):
        raise NotImplementedError

    def resolve_port(self):
        port = None
        srv_req = DNS.Request(qtype='srv', server=self.dns_server, timeout=0.1)
        try:
            srv_result = srv_req.req(self.get_real_host())
            for result in srv_result.answers:
                if result['typename'] == 'SRV':
                    port = result[u'data'][2]
        except (DNS.TimeoutError, DNS.Base.SocketError):
            pass
        self.port = port


class DjangoDatabaseJeteeServiceConfigResolver(JeteeServiceConfigResolver):
    def __init__(self, host, protocol):
        self.protocol = protocol
        self.host = host
        self.resolve_port()

    def render(self):
        return {
            'ENGINE': 'django.db.backends.{}'.format(self.protocol),
            # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'docker',  # Or path to database file if using sqlite3.
            'USER': 'docker',  # Not used with sqlite3.
            'PASSWORD': u'docker',  # Not used with sqlite3.
            'HOST': self.service_ip,  # Set to empty string for localhost. Not used with sqlite3.
            'PORT': self.port,  # Set to empty string for default. Not used with sqlite3.
        }


class RedisJeteeServiceConfigResolver(JeteeServiceConfigResolver):
    protocol = u'redis'

    def __init__(self, host, db=0):
        self.db = db
        self.host = host
        self.resolve_port()

    def render(self):
        return u'redis://{}:{}/{}'.format(self.service_ip, self.port, self.db)


class HaystackJeteeServiceConfigResolver(JeteeServiceConfigResolver):
    def __init__(self, host, engine, index_name):
        self.host = host
        self.engine = engine
        self.index_name = index_name
        self.resolve_port()

    def render(self):
        return {
            'ENGINE': self.engine,
            'URL': 'http://{}:{}'.format(self.service_ip, self.port),
            'INDEX_NAME': self.index_name,
        }