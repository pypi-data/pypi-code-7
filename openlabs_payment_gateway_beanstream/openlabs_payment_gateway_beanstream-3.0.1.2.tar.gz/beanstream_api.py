# -*- coding: utf-8 -*-
'''

    Beanstream API

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: BSD, see LICENSE for more details

'''
import requests
import urlparse
import urllib
import hashlib

from trytond.exceptions import UserError


class BeanstreamClient(object):
    """Beanstream request API

    :param merchant_id: 9 digit Merchant ID assigned by Beanstream
    """
    service_url = None

    #: The response code from the server which indicates success
    success_response_code = '1'

    #: Service version of the API
    service_version = '1.0'

    def __init__(
        self, merchant_id, test=False, pass_code=None, hash_key=None
    ):
        """
        :param merchant_id: Pass the merchant’s unique Beanstream
                            identification number. Please note that Beanstream
                            issues one merchant ID per currency. If the
                            merchant is processing in both Canadian and US
                            dollars, you will need to complete one full
                            integration per merchant ID number.

        .. tip::

            Note that this field is different from the merchantid field
            used in the Beanstream Process Transaction API

        :param test: Boolean to indicate if this is a test request.
        :param pass_code: Specify the API access passcode that has been
                          generated on the payment profile configuration page.
        :param hash_key: Specify the Hash Key that has been
                          saved in Beanstream account.
        """
        self.merchant_id = merchant_id
        self.test = test

        if not pass_code and not hash_key:
            # Atleast one should be there
            raise UserError(
                'Beanstream Error:', 'No validation method provided'
            )

        self.pass_code = pass_code
        self.hash_key = hash_key

    @property
    def payment_profile(self):
        return PaymentProfileAPI(
            self.merchant_id, self.test, pass_code=self.pass_code,
            hash_key=self.hash_key
        )

    @property
    def transaction(self):
        return TransactionAPI(
            self.merchant_id, self.test, pass_code=self.pass_code,
            hash_key=self.hash_key
        )

    def request(self, data, silent=False):
        """Send request to beanstream and return the response

        :param data: A dictionary in the format::
        """
        if 'merchant_id' not in data:
            data['merchantId'] = self.merchant_id

        data['responseFormat'] = 'QS'
        data['serviceVersion'] = self.service_version
        data['requestType'] = 'BACKEND'

        # Serialize Data
        data = urllib.urlencode(data)

        if self.pass_code:
            data += '&passCode=%s' % self.pass_code

        if self.hash_key:
            hashobj = hashlib.sha1()
            hashobj.update(data + self.hash_key)
            hash_value = hashobj.hexdigest()
            data += '&hashValue=%s' % hash_value

        result = requests.post(self.service_url, params=data)

        response = self.make_response(result.content)

        if not silent:
            self.handle_response(response)

        return response

    def handle_response(self, response):
        """
        Look into the response disctionary and raise them as exceptions.
        """
        if response['responseCode'] == self.success_response_code:
            return response

        error_message = response['responseMessage']
        if response.get('errorMessage'):
            error_message += '\n'
            error_message += response['errorMessage'].replace('<br>', '\n')

        raise UserError(
            'Beanstream Error: %s' % response['responseCode'], error_message
        )

    def make_response(self, response):
        """
        Parse the query string response.

        In addition to what parse_qs would do, the response is simplified by
        removing the list for items which have only 1 item in it.
        """
        # Parse the response and send it back
        rv = urlparse.parse_qs(response, keep_blank_values=True)
        return dict([
            (key, value[0]) if len(value) == 1 else (key, value)
            for key, value in rv.iteritems()
        ])


class CreditCard(object):
    """
    A credit card instance
    """
    def __init__(self, number, exp_year, exp_month, owner, cvd=None):
        """
        :param number: Specify the credit card number as it appears on the card
        :param owner: Specify the name of the card owner as it appears on their
                      credit card.
        :param exp_month: Indicate the credit card expiration month
        :param exp_year: Indicate the expiration year.
        """
        self.number = number
        self.owner = owner
        assert len(exp_month) == 2, "Exp. Month should be in two digit format"
        self.exp_month = exp_month
        assert len(exp_year) == 2, "Exp. Year should be in two digit format"
        self.exp_year = exp_year
        self.cvd = cvd

    def as_variables_dict(self):
        """
        Returns a dictioanry with the variables that beanstream understands
        """
        rv = {
            'trnCardOwner': self.owner,
            'trnCardNumber': self.number,
            'trnExpMonth': self.exp_month,
            'trnExpYear': self.exp_year,
        }
        if self.cvd:
            rv['trnCardCvd'] = self.cvd
        return rv


class TransactionAPI(BeanstreamClient):
    """
    Transaction chargin API

    http://developer.beanstream.com/wp-content/uploads/sites/3/2013/09/BEAN_API_Integration.pdf
    """
    service_url = "https://www.beanstream.com/scripts/process_transaction.asp"

    def request(self, data):
        """
        Add merchant_id
        """
        data['merchant_id'] = self.merchant_id
        return super(TransactionAPI, self).request(data)

    def handle_response(self, response):
        """
        Dont handle responses since they carry invaluable information that
        needs to be logged
        """
        pass

    def pre_authorize(self, transaction, card=None):
        """
        Pre authorization
        """
        data = {
            'trnType': 'PA',
        }
        data.update(transaction.get_beanstream_transaction_dict())

        if transaction.payment_profile:
            # Process transaction on stored card
            return

        if not card:
            # Neither a profile based transaction, nor is a card given
            # BLOW UP!!
            transaction.raise_user_error('no_card_or_profile')

        # Perform the card transaction
        data.update(card.as_variables_dict())
        data.update(transaction.address.get_beanstream_contact_dict())

        return self.request(data)

    def purchase(self, transaction, card):
        """
        Complete purchase
        """
        data = {'trnType': 'P'}

        data.update(transaction.get_beanstream_transaction_dict())

        if transaction.payment_profile:
            # Process transaction on stored card
            #
            # The customerCode is what decides the payment profile and the
            # module uses the provider reference as the customer code
            customer_code = transaction.payment_profile.provider_reference
            data['customerCode'] = customer_code
            return self.request(data)

        if not card:
            # Neither a profile based transaction, nor is a card given
            # BLOW UP!!
            transaction.raise_user_error('no_card_or_profile')

        # Perform the card transaction
        data.update(card.as_variables_dict())
        data.update(transaction.address.get_beanstream_contact_dict())

        return self.request(data)

    def query(self, order_number):
        """Get the status of an order being processed or not

        :param order_number: Order number
        """
        data = {
            'trnType': 'Q',
            'trnOrderNumber': order_number,
        }
        return self.request(data)


class BeanstreamException(Exception):
    pass


class PaymentProfileAPI(BeanstreamClient):
    """
    For creating customer shopping profiles.

    Refer: http://developer.beanstream.com/wp-content/uploads/sites/
           3/2013/09/BEAN_Payment_Profiles.pdf
    """

    service_url = 'https://www.beanstream.com/scripts/payment_profile.asp'

    def create(self, card, address, validate=False):
        """
        Create a profile tied to one individual assigning and validating a
        single credit card.
        """
        data = {
            'operationType': 'N',
        }
        data.update(card.as_variables_dict())
        data.update(address.get_beanstream_contact_dict())
        if validate:
            data['cardValidation'] = '1'
        return self.request(data)

    def activate(self, profile):
        """
        Activate a profile
        """
        pass

    def disable(self, profile):
        """
        Disable a profile
        """
        pass

    def close(self, profile):
        """
        Close a payment profile
        """
        pass
