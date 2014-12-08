import requests
from pyslaquery import exception as pyslaquery_exceptions


class SlackAPIConnection(object):
    """
    Logic abstraction around requests module and connectivity to Slack API.
    """

    def __init__(self, base, token):
        self.base = base
        self.token = token

    def create_post_request(self, method, params):
        """
        Create POST request to the Slack API
        :param method: Slack API method
        :param params: params to include with the request
        :return: requests.Response object
        """
        params.update({
            'token': self.token
        })
        url = "%s/%s" % (self.base, method)
        result = requests.post(url, data=params, verify=False)

        """
        API Basics from api.slack.com states that:
        "ok" : true - Request is OK.
        "ok" : false - Excepction.
        """
        if not result.json()['ok']:
            raise pyslaquery_exceptions.SlackAPIError(result.json()['error'])

        return result

    def create_get_request(self, method, params):
        """
        Create GET request to the Slack API
        :param method: Slack API method
        :param params: params to include with the request
        :return: requests.Response object
        """
        params.update({
            'token': self.token
        })
        url = "%s/%s" % (self.base, method)
        result = requests.post(url, data=params, verify=False)

        if not result.json()['ok']:
            raise pyslaquery_exceptions.SlackAPIError(result.json()['error'])

        return result
