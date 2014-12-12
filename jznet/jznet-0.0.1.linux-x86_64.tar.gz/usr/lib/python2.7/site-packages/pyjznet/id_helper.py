# coding: utf-8
from __future__ import print_function

import uuid


def generate_request_id():
    return str(uuid.uuid4())