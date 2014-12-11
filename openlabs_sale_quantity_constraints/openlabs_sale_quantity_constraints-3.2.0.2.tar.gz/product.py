# -*- coding: utf-8 -*-
"""
    product.py

    :copyright: (c) 2012-2014 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
from trytond.pool import PoolMeta
from trytond.model import fields

__metaclass__ = PoolMeta
__all__ = ['Product']


class Product:
    "Product"
    __name__ = 'product.product'

    order_minimum = fields.Float('Minimum Quantity')
    order_multiple = fields.Float('Quantity Multiple')
    order_maximum = fields.Float('Maximum Quantity')
