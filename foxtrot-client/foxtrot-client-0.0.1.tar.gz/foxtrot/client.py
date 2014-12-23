import requests, json
from urllib import urlencode
from _required_fields import check_required
from response import FoxtrotResponse

class Foxtrot(object):
  """Foxtrot API Client"""

  host = 'app.foxtrot.io'
  ssl = True

  def __init__(self, api_key, version='v1'):
    self.api_key = api_key
    self.version = version
    self.headers = {'content-type': 'application/json'}

  def __build_url(self, endpoint, args):
    proto = "https" if self.ssl else "http"
    args['key'] = self.api_key
    query = urlencode(args)
    return "{}://{}/api/{}/{}?{}".format(proto, self.host, self.version, endpoint, query)

  def __get_request(self, endpoint, args):
    url = self.__build_url(endpoint, args)
    response = requests.get(url, headers=self.headers)
    return response.json()

  def __post_request(self, endpoint, data, args):
    url = self.__build_url(endpoint, args)
    response = requests.post(url, data=json.dumps(data), headers=self.headers)
    return response.json()

  def _poll(self, endpoint, txid, args={}):
    resp = self.__get_request(endpoint, {'txid': txid})
    return FoxtrotResponse.response_for(endpoint, resp, self)

  @check_required
  def optimize(self, data, args={}):
    resp = self.__post_request('optimize', data, args)
    return FoxtrotResponse.response_for('optimize', resp, self)
