# -*- coding: utf-8 -*-
"""
    sale.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.transaction import Transaction
from trytond.pyson import Eval, Or

__metaclass__ = PoolMeta
__all__ = ['SaleLine']


class SaleLine:
    __name__ = 'sale.line'

    available_stock_qty = fields.Function(
        fields.Float(
            'Available Quantity',
            digits=(16, Eval('unit_digits', 2)),
            states={
                'invisible': Or(
                    Eval('type') != 'line',
                    Eval('sale_state') == 'done'
                ),
            },
            depends=['type', 'unit_digits', 'sale_state']
        ),
        'on_change_with_available_stock_qty'
    )

    sale_state = fields.Function(
        fields.Char('Sale State'), 'get_sale_state'
    )

    @fields.depends('_parent_sale.warehouse', 'product', 'type')
    def on_change_with_available_stock_qty(self, name=None):
        """
        Returns the available stock to process a Sale
        """
        Date = Pool().get('ir.date')

        if self.type == 'line' and self.product and self.sale.warehouse:
            with Transaction().set_context(
                locations=[self.sale.warehouse.id],
                stock_skip_warehouse=True,
                stock_date_end=Date.today(),
                stock_assign=True
            ):
                return self.product.quantity

    def get_sale_state(self, name):
        """
        Returns the state of the Sale
        """
        return self.sale and self.sale.state
