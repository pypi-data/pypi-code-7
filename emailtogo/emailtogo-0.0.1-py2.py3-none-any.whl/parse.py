# -*- coding: utf-8 -*-

import os.path

KNOWN_SERVICES = {}

with open(os.path.join(os.path.dirname(__file__), 'KNOWN_SERVICES')) as fp:
    KNOWN_SERVICES.update(dict([line.split() for line in fp]))


def parse_address(address):
    _, service = address.lower().split('@')

    if service in KNOWN_SERVICES:
        return KNOWN_SERVICES[service]

    return "mail." + service
