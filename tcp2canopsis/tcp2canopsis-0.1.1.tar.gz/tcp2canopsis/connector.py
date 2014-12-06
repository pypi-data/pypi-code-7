# -*- coding: utf-8 -*-

from tcp2canopsis.errors import ConnectorError
from twisted.protocols import basic

from kombu import Connection
from kombu.pools import producers

import json


class Connector(basic.LineReceiver):
    def __init__(self, factory, addr, amqpuri):
        self.factory = factory
        self.address = addr
        self.amqpuri = amqpuri

    def connectionMade(self):
        self.factory.clients.add(self)

    def connectionLost(self, reason):
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        try:
            event = self.parse_event(line)
            rk = self.generate_rk(event)
            self.send_event(rk, event)

        except ConnectorError as err:
            print(err)

    def parse_event(self, line):
        try:
            event = json.loads(line)

        except ValueError as err:
            raise ConnectorError('Invalid event: {0}'.format(str(err)))

        return event

    def generate_rk(self, event):
        try:
            rk = '{}.{}.{}.{}.{}'.format(
                event['connector'],
                event['connector_name'],
                event['event_type'],
                event['source_type'],
                event['component']
            )

            if event['source_type'] == 'resource':
                rk = '{}.{}'.format(rk, event['resource'])

        except KeyError as err:
            raise ConnectorError('Missing key in event: {0}'.format(str(err)))

        return rk

    def send_event(self, rk, event):
        try:
            with Connection(self.amqpuri) as conn:
                with producers[conn].acquire(block=True) as producer:
                    producer.publish(
                        event,
                        serializer='json',
                        exchange='canopsis.events',
                        routing_key=rk
                    )

        except Exception as err:
            raise ConnectorError('Cannot send event: {0}'.format(str(err)))
