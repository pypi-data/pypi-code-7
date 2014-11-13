import pika
import json


class EventSender(object):
    def __init__(self, login, password, host, virtual_host, exchange, exchange_options=None):
        self.exchange = exchange
        if not exchange_options:
            exchange_options = {
                'auto_delete': False,
                'type': 'topic'
            }
        conn_params = pika.ConnectionParameters(
            host=host,
            virtual_host=virtual_host,
            credentials=pika.PlainCredentials(login, password)
        )
        self.connection = pika.BlockingConnection(conn_params)

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, **exchange_options)

    def __del__(self):
        self.connection.close()

    def push(self, routing_key, message):
        dumped_message = json.dumps(message)
        self.push_text(routing_key, dumped_message)

    def push_text(self, routing_key, message):
        self.channel.basic_publish(exchange=self.exchange, routing_key=routing_key, body=message)


class EventListener(EventSender):
    def __init__(self, login, password, host, virtual_host, exchange, queue, bindings, exchange_options=None):
        super(EventListener, self).__init__(login, password, host, virtual_host, exchange,
                                            exchange_options=exchange_options)
        self.queue = queue
        self.channel.queue_declare(queue, exclusive=False)

        for binding_key in bindings:
            self.channel.queue_bind(exchange=exchange,
                                    queue=queue,
                                    routing_key=binding_key)

    def register_callback(self, callback, no_ack=True):
        self.channel.basic_consume(callback, queue=self.queue, no_ack=no_ack)
        self.channel.start_consuming()
