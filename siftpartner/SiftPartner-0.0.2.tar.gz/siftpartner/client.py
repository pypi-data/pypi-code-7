import json
import requests

import siftpartner
from . import version
from . import response

API_URL = "https://partner.siftscience.com/v%s" % version.API_VERSION
API_TIMEOUT = 2


class Client(object):
    def __init__(self, api_key=None, partner_id=None):
        """Initialize the client.

        Args:
            api_key: Your Sift Science Partner API key associated with your partner
                account. This can be found at https://siftscience.com//console/api-keys
            id: Your partner account id, which can be found at https://siftscience.com/console/settings
        """

        # set api key to module scoped key if not specified
        if api_key is None:
            api_key = siftpartner.api_key

        # set partner id to module scoped key if not specified
        if partner_id is None:
            partner_id = siftpartner.partner_id

        if not isinstance(api_key, str) or len(api_key.strip()) == 0:
            raise RuntimeError("api_key must be a non-empty string")

        if not isinstance(partner_id, str) or len(partner_id.strip()) == 0:
            raise RuntimeError("partner_id must be a non-empty string")

        self.api_key = api_key
        self.partner_id = partner_id

    @staticmethod
    def user_agent():
        return 'SiftScience/v%s sift-partner-python/%s' % (version.API_VERSION, version.VERSION)

    def accounts_url(self):
        return API_URL + "/partners/%s/accounts" % self.partner_id

    def notifications_config_url(self):
        return API_URL + "/accounts/%s/config" % self.partner_id

    # Creates a new merchant account under the given partner.
    # == Parameters:
    # site_url
    # the url of the merchant site
    # site_email
    # an email address for the merchant
    # analyst_email
    # an email address which will be used to log in at the Sift Console
    # password
    # password (at least 10 chars) to be used to sign into the Console
    #
    # When successful, returns a including the new account id and credentials.
    # When an error occurs, The exception is raised.
    def new_account(self, site_url, site_email, analyst_email, password):
        properties = {'site_url': site_url,
                      'site_email': site_email,
                      'analyst_email': analyst_email,
                      'password': password
        }

        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Basic ' + self.api_key,
                   'User-Agent': self.user_agent()
        }

        params = {}
        try:
            res = requests.post(self.accounts_url(),
                                data=json.dumps(properties),
                                headers=headers,
                                timeout=API_TIMEOUT,
                                params=params
            )
            return response.Response(res)
        except requests.exceptions.RequestException as e:
            raise e

    # Gets a listing of the ids and keys for all merchant accounts that have
    # been created by this partner.
    #
    # When successful, returns a hash including the key :data, which is an
    # array of account descriptions. (Each element has the same structure as a
    # single response from new_account).
    def get_accounts(self):
        headers = {'Authorization': 'Basic ' + self.api_key,
                   'User-Agent': self.user_agent()
        }

        try:
            res = requests.get(self.accounts_url(),
                               headers=headers,
                               timeout=API_TIMEOUT
            )
            return response.Response(res)
        except requests.exceptions.RequestException as e:
            raise e

    # Updates the configuration which controls http notifications for all merchant
    # accounts under this partner.
    #
    # == Parameters
    # cfg
    # A Hash, with keys :http_notification_url and :http_notification_threshold
    # The value of the notification_url will be a url containing the string '%s' exactly once.
    #   This allows the url to be used as a template, into which a merchant account id can be substituted.
    #   The  notification threshold should be a floating point number between 0.0 and 1.0
    def update_notification_config(self, cfg):
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Basic ' + self.api_key,
                   'User-Agent': self.user_agent()
        }

        try:
            res = requests.put(self.notifications_config_url(),
                               data=json.dumps(cfg),
                               headers=headers,
                               timeout=API_TIMEOUT
            )
            return response.Response(res)
        except requests.exceptions.RequestException as e:
            raise e








