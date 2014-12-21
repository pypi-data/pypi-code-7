# -*- coding: utf-8 -*-
'''

    Payment Gateway

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: BSD, see LICENSE for more details

'''
from trytond.pool import Pool
from .transaction import PaymentGatewayBeanstream, BeanstreamTransaction, \
     AddPaymentProfileView, AddPaymentProfile, Address


def register():
    Pool.register(
        PaymentGatewayBeanstream,
        AddPaymentProfileView,
        BeanstreamTransaction,
        Address,
        module='payment_gateway_beanstream', type_='model'
    )
    Pool.register(
        AddPaymentProfile,
        module='payment_gateway_beanstream', type_='wizard'
    )
