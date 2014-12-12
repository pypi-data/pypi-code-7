# -*- coding: utf-8 -*-

from twisted.internet import protocol


class ConnectorFactory(protocol.Factory):
    def __init__(self, amqpuri, token, connector):
        self.clients = set()
        self.connector = connector
        self.amqpuri = amqpuri
        self.token = token

    def buildProtocol(self, addr):
        return self.connector(self, addr)
