
from .api import User, Invoice, PaymentSettings


class Client(object):
    """Returns client object to access the api methods"""

    def __init__(self, token):
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Token %s' % self.token
        }

    def user(self):
        """Client object to handle user operations"""

        return User(self.headers)

    def invoice(self):
        """Client object to handle invoice operations"""

        return Invoice(self.headers)

    def payment(self):
        """PaymentSettings object to handle payment operations"""

        return PaymentSettings(self.headers)
