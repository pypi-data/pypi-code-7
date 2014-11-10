from pprint import pprint

from robokassa.signals import result_received


def payment_received(sender, **kwargs):
    pprint(kwargs)


result_received.connect(payment_received)
