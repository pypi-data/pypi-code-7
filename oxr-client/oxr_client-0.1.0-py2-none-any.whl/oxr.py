import requests
from datetime import datetime
from copy import deepcopy

from .exceptions import OXRError


class OXR(object):
    BASE_URL = 'https://openexchangerates.org/api/'

    def __init__(self, app_id, base='USD'):
        self._app_id = app_id
        self._base = base
        self._rates = {}

    @property
    def rates(self):
        return deepcopy(self._rates)

    def latest(self, base=None):
        base = base or self._base
        self._rates = self.__fetch('latest.json', base=base)
        return self.rates

    def historical(self, date, base=None):
        base = base or self._base
        date_str = self.__format_date_to_string(date)
        return self.__fetch('historical/{0}.json'.format(date_str), base=base)

    def convert(self, amount, to, frm=None):
        """Convert is a convenience function that will get the latest rates
        and perform a conversion. Note that calling this function will make
        a request each time. If multiple conversions need to be made, call
        latest and use the returned rates"""
        rates = self.latest(frm)
        try:
            return amount * rates[to]
        except KeyError:
            raise ValueError("Invalid 'to' currency code")

    def __fetch(self, endpoint, **kwargs):
        url = self.BASE_URL + endpoint
        params = {'app_id': self._app_id}
        params.update(kwargs)

        response = requests.get(url, params=params)
        try:
            return self.__parse(response.json())
        except (ValueError, UnicodeDecodeError):
            raise OXRError("internal_server_error", 500, "Unknown response received from API")

    def __parse(self, body):
        if body.get('error', False) is True:
            raise OXRError(body['message'], body['status'], body['description'])

        return body['rates']

    def __format_date_to_string(self, date):
        """Date must be in format YYYY-MM-DD for oxr api. If a string
        is passed in, it is assumed to be in this format"""
        if isinstance(date, basestring):
            return date
        elif isinstance(date, datetime):
            return date.strftime('%Y-%m-%d')
        else:
            raise TypeError("{0} is not string or datetime".format(repr(date)))
