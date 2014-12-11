# -*- coding: utf-8 -*-
'''
    __init__.py

    :copyright: (c) 2012-2014 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details
'''
from trytond.pool import Pool
from product import Product
from sale import Sale, SaleLine


def register():
    Pool.register(
        Product,
        Sale,
        SaleLine,
        module='sale_quantity_constraints', type_='model'
    )
