# -*- coding: utf-8 -*-

from twisted.internet import protocol


class ConnectorFactory(protocol.Factory):
    def __init__(self, amqpuri, connector):
        self.clients = set()
        self.connector = connector
        self.amqpuri = amqpuri

    def buildProtocol(self, addr):
        return self.connector(self, addr, self.amqpuri)
