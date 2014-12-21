# -*- coding: utf-8 -*-
'''

    Payment Gateway Transaction

    :copyright: (c) 2013-2014 by Openlabs Technologies & Consulting (P) Ltd.
    :license: BSD, see LICENSE for more details

'''
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval
from trytond.model import fields

from .beanstream_api import BeanstreamClient, CreditCard


__all__ = [
    'PaymentGatewayBeanstream', 'BeanstreamTransaction',
    'AddPaymentProfileView', 'Address', 'AddPaymentProfile',
]
__metaclass__ = PoolMeta

BEANSTREAM_STATES = {
    'required': Eval('provider') == 'beanstream',
    'invisible': Eval('provider') != 'beanstream'
}


class PaymentGatewayBeanstream:
    "Beanstream Gateway Implementation"
    __name__ = 'payment_gateway.gateway'

    beanstream_merchant_id = fields.Char(
        'Merchant ID', states=BEANSTREAM_STATES, depends=['provider']
    )
    beanstream_currency = fields.Many2One(
        'currency.currency', 'Currency', states=BEANSTREAM_STATES,
        depends=['provider']
    )
    beanstream_auth_mechanism = fields.Selection([
        ('passcode', 'Passcode'),
        ('hash', 'Hash SHA1')
    ], 'Authentication Mechanism', states=BEANSTREAM_STATES)

    beanstream_pass_code = fields.Char(
        'Pass Code', states={
            'required': (
                (Eval('provider') == 'beanstream') &
                (Eval('beanstream_auth_mechanism') == 'passcode')
            ),
            'invisible': ~(
                (Eval('provider') == 'beanstream') &
                (Eval('beanstream_auth_mechanism') == 'passcode')
            )
        }, depends=['provider', 'beanstream_auth_mechanism']
    )
    beanstream_hash_key = fields.Char(
        "Hash Key", states={
            'required': (
                (Eval('provider') == 'beanstream') &
                (Eval('beanstream_auth_mechanism') == 'hash')
            ),
            'invisible': ~(
                (Eval('provider') == 'beanstream') &
                (Eval('beanstream_auth_mechanism') == 'hash')
            )
        }, depends=['provider', 'beanstream_auth_mechanism']
    )

    @staticmethod
    def default_auth_mechanism():
        return 'passcode'

    @classmethod
    def get_providers(cls, values=None):
        """
        Downstream modules can add to the list
        """
        rv = super(PaymentGatewayBeanstream, cls).get_providers()
        beanstream_record = ('beanstream', 'Beanstream')
        if beanstream_record not in rv:
            rv.append(beanstream_record)
        return rv

    def get_methods(self):
        if self.provider == 'beanstream':
            return [
                ('credit_card', 'Credit Card - Beanstream'),
            ]
        return super(PaymentGatewayBeanstream, self).get_methods()

    def get_beanstream_client(self):
        """
        Returns a Beanstream client API
        """
        validation_params = {}
        if self.beanstream_auth_mechanism == 'passcode':
            validation_params['pass_code'] = self.beanstream_pass_code
        elif self.beanstream_auth_mechanism == 'hash':
            validation_params['hash_key'] = self.beanstream_hash_key

        return BeanstreamClient(
            merchant_id=self.beanstream_merchant_id,
            test=self.test,
            **validation_params
        )


class BeanstreamTransaction:
    """
    Implement the authorize and capture methods
    """
    __name__ = 'payment_gateway.transaction'

    def get_beanstream_transaction_dict(self):
        """
        Returns a dictionary of variables as required for the beanstream
        request
        """
        Currency = Pool().get('currency.currency')

        res = {
            'requestType': 'BACKEND',
            'trnOrderNumber': self.uuid,
            'trnAmount': str(Currency.compute(
                self.currency, self.amount, self.gateway.beanstream_currency)
            ),
        }
        return res

    def authorize_beanstream(self, credit_card=None):
        """
        Authorize using beanstream for the specific transaction.

        :param credit_card: An instance of CreditCardView
        """
        raise self.raise_user_error('feature_not_available')

    def capture_beanstream(self, card_info=None):
        """
        Capture using beanstream for the specific transaction.

        :param card_info: An instance of CreditCardView
        """
        TransactionLog = Pool().get('payment_gateway.transaction.log')

        credit_card = None
        if card_info is not None:
            credit_card = CreditCard(
                card_info.number,
                str(card_info.expiry_year)[-2:],
                card_info.expiry_month,
                card_info.owner,
                card_info.csc,
            )

        client = self.gateway.get_beanstream_client()
        result = client.transaction.purchase(self, credit_card)

        # save the result to the logs
        TransactionLog.serialize_and_create(self, result)

        # TODO: Update the timestamp with the trnDate return value from
        # beanstream sent in the format '%m/%d/%Y %I:%M:%S %p' but the
        # timezone is not mentioned in the docs

        self.provider_reference = result['trnId']
        if result['trnApproved'] == '1':
            self.state = 'completed'
            self.safe_post()
        else:
            self.state = 'failed'
        self.save()

    def retry_beanstream(self, credit_card=None):
        """
        Authorize using beanstream for the specific transaction.

        :param credit_card: An instance of CreditCardView
        """
        raise self.raise_user_error('feature_not_available')

    def settle_beanstream(self):
        """
        Settle the authporized payment
        """
        raise self.raise_user_error('feature_not_available')

    def update_beanstream(self):
        """
        Update the status of the transaction from beanstream
        """
        TransactionLog = Pool().get('payment_gateway.transaction.log')

        client = self.gateway.get_beanstream_client()

        result = client.transaction.query(self.uuid)

        # save the result to the logs
        TransactionLog.serialize_and_create(self, result)

        print result


class AddPaymentProfileView:
    __name__ = 'party.payment_profile.add_view'

    @classmethod
    def get_providers(cls):
        """
        Return the list of providers who support credit card profiles.
        """
        res = super(AddPaymentProfileView, cls).get_providers()
        res.append(('beanstream', 'Beanstream'))
        return res


class Address:
    """
    Add beanstream contact details fetching ability to address
    """
    __name__ = 'party.address'

    def get_beanstream_contact_dict(self):
        """
        Returns a dictionary with keys as beanstream variables and
        corresponding values from address and party.
        """
        res = {
            'ordName': self.name or self.party.name,
            'ordAddress1': self.street,
            'ordAddress2': self.streetbis,
            'ordCity': self.city,
            'ordPostalCode': self.zip,
            'ordEmailAddress': self.party.email,
            'ordPhoneNumber': self.party.phone,
            'ordCountry': self.country and self.country.code,
        }
        if self.country and self.country.code in ('US', 'CA'):
            # For US and Canada send province code else --
            res['ordProvince'] = self.subdivision and self.subdivision.code[-2:]
        else:
            res['ordProvince'] = '--'
        return dict((k, v) for k, v in res.iteritems() if v)


class AddPaymentProfile:
    """
    Add a payment profile
    """
    __name__ = 'party.party.payment_profile.add'

    def transition_add_beanstream(self):
        """
        Handle the case if the profile should be added for beanstream
        """
        card_info = self.card_info

        client = card_info.gateway.get_beanstream_client()
        cc = CreditCard(
            card_info.number,
            str(card_info.expiry_year)[-2:],    # 4 digit to 2 digit
            card_info.expiry_month,
            card_info.owner,
            card_info.csc,
        )
        result = client.payment_profile.create(cc, card_info.address)

        # Beanstream allows a profile functionality where multiple cards
        # can be registered against a single person. While the feature
        # looks close to the payment_proifle implementation, it is not
        # possible to maintain such an integration. So in practive this
        # module uses the customerCode automatically generated by
        # beanstream as the reference for each card.
        #
        # In other words, each profile is maintained as a separate profile
        # on beanstream
        return self.create_profile(result['customerCode'])
