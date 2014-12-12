# -*- coding: utf-8 -*-

from tcp2canopsis.factory import ConnectorFactory
from tcp2canopsis.connector import Connector
from twisted.internet import reactor, endpoints


def run_daemon(port, amqpuri, token):
    server = 'tcp:{0}'.format(port)

    factory = ConnectorFactory(amqpuri, token, Connector)
    endpoint = endpoints.serverFromString(reactor, server)
    endpoint.listen(factory)
    reactor.run()
