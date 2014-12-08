# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2014 by Lava Lab Software Pty Ltd
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from party import Party


def register():
    Pool.register(
        Party,
        module='party_abn', type_='model'
    )
