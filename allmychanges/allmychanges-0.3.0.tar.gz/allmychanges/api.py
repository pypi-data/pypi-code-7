import requests
from urllib import urlencode

from .config import get_option

_BASE_URL = 'http://allmychanges.com/v1'


class ApiError(RuntimeError):
    def __init__(self, message, response):
        super(ApiError, self).__init__(message)
        self.response = response


def _call(method, config, handle, data=None):
    token = get_option(config, 'token')
    base_url = get_option(config, 'base_url', _BASE_URL)

    if handle.startswith('http'):
        url = handle
    else:
        url = base_url + handle

    func = getattr(requests, method)
    response = func(url,
                    headers={'Authorization':
                             'Bearer ' + token},
                    data=data)

    if response.status_code >= 400:
        raise ApiError(response.reason, response)

    return response.json()

_get = lambda *args, **kwargs: _call('get', *args, **kwargs)
_post = lambda *args, **kwargs: _call('post', *args, **kwargs)
_put = lambda *args, **kwargs: _call('put', *args, **kwargs)


def get_changelogs(config, **params):
    """Returns list of changelogs.
    Params could be: namespace and name or tracked=True
    """
    handle = '/changelogs/'
    return _get(config, handle + '?' + urlencode(params))

def create_changelog(config, pk, source):
    return _post(config, '/changelogs/',
                 data=dict(namespace=pk[0],
                           name=pk[1],
                           source=source))

def update_changelog(config, changelog, namespace, name, source):
    return _put(config, changelog['resource_uri'],
                 data=dict(namespace=namespace,
                           name=name,
                           source=source))


def track_changelog(config, changelog):
    return _post(config, changelog['resource_uri'] + 'track/')


def guess_source(config, namespace, name):
    response = _get(config, '/search-autocomplete/?' + urlencode(
        dict(q='{0}/{1}'.format(namespace, name))))
    return [item['name']
            for item in response['results']]
