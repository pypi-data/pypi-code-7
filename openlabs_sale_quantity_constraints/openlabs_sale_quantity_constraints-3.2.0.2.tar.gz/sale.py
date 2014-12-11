# -*- coding: utf-8 -*-
"""
    sale.py

    :copyright: (c) 2012-2014 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
from trytond.pool import PoolMeta
from trytond.model import fields

__metaclass__ = PoolMeta
__all__ = ['Sale', 'SaleLine']


class Sale:
    "Sale"
    __name__ = 'sale.sale'

    qty_strict_check = fields.Boolean('Ensure Strict Quantity Check')

    @staticmethod
    def default_qty_strict_check():
        return True


class SaleLine:
    'Sale Line'
    __name__ = 'sale.line'

    @classmethod
    def __setup__(cls):
        super(SaleLine, cls).__setup__()
        cls._error_messages.update({
            'wrong_minimum': 'Minimum Order Quantity for Product %s is %s %s',
            'wrong_multiple':
                'Order Quantity for Product %s must be a multiple of %s',
            'wrong_maximum': 'Maximum Order Quantity for Product %s is %s %s'
        })

    @classmethod
    def validate(cls, lines):
        super(SaleLine, cls).validate(lines)
        for line in lines:
            line.check_qty_minimum()
            line.check_qty_multiple()
            line.check_qty_maximum()

    def check_qty_minimum(self):
        """Make sure the ordered quantity is more than the minimum
            qunantity specified in the corresponding product
        """
        if not self.sale.qty_strict_check:
            return
        if self.quantity and self.product and self.product.order_minimum \
                and self.quantity < self.product.order_minimum:
            self.raise_user_error('wrong_minimum', error_args=(
                self.product.name, self.product.order_minimum,
                self.product.sale_uom.name
            ))

    def check_qty_multiple(self):
        """Make sure the ordered quantity is a multiple of the multiple
            qunantity specified in the corresponding product
        """
        if not self.sale.qty_strict_check:
            return
        if self.quantity and self.product and self.product.order_multiple \
                and (self.quantity % self.product.order_multiple != 0):
            self.raise_user_error('wrong_multiple', error_args=(
                self.product.name, self.product.order_multiple
            ))

    def check_qty_maximum(self):
        """Make sure the ordered quantity is less than the maximum
            qunantity specified in the corresponding product
        """
        if not self.sale.qty_strict_check:
            return
        if self.quantity and self.product and self.product.order_maximum \
                and self.quantity > self.product.order_maximum:
            self.raise_user_error('wrong_maximum', error_args=(
                self.product.name, self.product.order_maximum,
                self.product.sale_uom.name
            ))
