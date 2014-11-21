import requests
import json
import logging

try:
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured
    PYGNIP_CONFIG = settings.PYGNIP_CONFIG
except (ImportError, AttributeError):
    from .settings import PYGNIP_CONFIG

logger = logging.getLogger(__name__)


class Config(object):
    """ Set config in Django settings or gnip_config.ini in ~/.config """
    def __init__(self, *args, **kwargs):
        if isinstance(PYGNIP_CONFIG, dict):
            obj = PYGNIP_CONFIG[kwargs['config']]
        else:
            obj = dict(PYGNIP_CONFIG.items(kwargs['config']))
        self.account = obj.get('account', None)
        self.username = obj.get('username', None)
        self.password = obj.get('password', None)
        self.data_source = obj.get('data_source', None)
        self.stream_label = obj.get('stream_label', None)

        self.APIs = {
            'UsageAPI': {
                'url': ('https://account-api.gnip.com/accounts/%s/usage.json'
                        % (self.account)),
                'controller': _UsageAPI
                },
            'SearchAPI': {
                'url': ('https://search.gnip.com/accounts/%s/search/%s.json'
                        % (self.account, self.stream_label)),
                'controller': _SearchAPI
                },
            'SearchAPICount': {
                'url': ('https://search.gnip.com/accounts/%s/search/%s/counts.json'
                        % (self.account, self.stream_label)),
                'controller': _SearchAPI
                },
            'PowertrackAPI': {
                'url': ('https://stream.gnip.com:443/accounts/%s/publishers/%s/streams/track/%s.json'
                        % (self.account, self.data_source, self.stream_label)),
                'controller': _PowerTrackAPI
                },
            'PowertrackAPIRules': {
                'url': ('https://api.gnip.com:443/accounts/%s/publishers/%s/streams/track/%s/rules.json'
                        % (self.account, self.data_source, self.stream_label)),
                'controller': _PowerTrackAPI
                },
        }


class AllAPIs(object):
    """ Generic client """

    def __init__(self, *args, **kwargs):
        self.config = Config(config=kwargs.get('config', 'DEFAULT'))

    def get_connection(self, **kwargs):
        try:
            return requests.get(self.base_api_url,
                                auth=(self.config.username,
                                      self.config.password),
                                params=kwargs
                                )
        except Exception as e:
            logger.error(e)

    def post_connection(self, **kwargs):
        try:
            return requests.post(self.base_api_url,
                                 auth=(self.config.username,
                                       self.config.password),
                                 data=json.dumps(kwargs, ensure_ascii=False).encode('utf8')
                                 )
        except Exception as e:
            logger.error(e)

    def delete_connection(self, **kwargs):
        try:
            return requests.delete(self.base_api_url,
                                   auth=(self.config.username,
                                         self.config.password),
                                   data=json.dumps(kwargs, ensure_ascii=False).encode('utf8')
                                   )
        except Exception as e:
            logger.error(e)

    def api(self, api):
        try:
            self.base_api_url = self.config.APIs[api]['url']
            controller = self.config.APIs[api]['controller'](self.config,
                                                             self.base_api_url)
        except (KeyError):
            raise Exception('%s is not a valid api.' % api)
        else:
            return controller


class _UsageAPI(AllAPIs):
    """ Usage API - http://support.gnip.com/apis/usage_api.html """

    def __init__(self, config, base_api_url, *args, **kwargs):
        self.config = config
        self.base_api_url = base_api_url

    def get_usage(self, decode_json=True, **kwargs):
        if decode_json:
            return self.get_connection(**kwargs).json()
        else:
            return self.get_connection(**kwargs)


class _SearchAPI(AllAPIs):
    """ Search API http://support.gnip.com/apis/search_api/api_reference.html """

    def __init__(self, config, base_api_url, *args, **kwargs):
        self.base_api_url = base_api_url
        self.config = config

    def search_count(self, decode_json=True, **kwargs):
        if decode_json:
            return self.post_connection(**kwargs).json()
        else:
            return self.post_connection(**kwargs)

    def max_results_only(self, decode_json=True, **kwargs):
        """ gets all tweets to max specified """
        if decode_json:
            return self.post_connection(**kwargs).json()
        else:
            return self.post_connection(**kwargs)

    def all_results(self, **kwargs):
        """ gets all tweets in memory"""
        tweets = []
        gnip_response = self.post_connection(**kwargs).json()

        if 'results' in gnip_response:
            tweets.extend(gnip_response['results'])

            while True:

                if 'next' in gnip_response:
                    kwargs['next'] = gnip_response['next']
                    gnip_response = self.post_connection(**kwargs).json()
                    tweets.extend(gnip_response['results'])
                else:
                    break

        return tweets    

    def iterate_all_results(self, **kwargs):
        """ generator method """
        gnip_response = self.post_connection(**kwargs).json()
        first_iteration = True

        while True:
            if first_iteration and 'next' in gnip_response:
                first_iteration = False
                yield gnip_response
            elif 'next' in gnip_response:
                kwargs['next'] = gnip_response['next']
                gnip_response = self.post_connection(**kwargs).json()
                if 'next' not in gnip_response:
                    yield gnip_response
                    break
                else:
                    yield gnip_response
            else:
                yield gnip_response
                break


class _PowerTrackAPI(AllAPIs):
    """ PowerTrack API http://support.gnip.com/apis/powertrack/api_reference.html """

    def __init__(self, config, base_api_url, *args, **kwargs):
        self.base_api_url = base_api_url
        self.config = config

    def get_rules(self, decode_json=True, **kwargs):
        if decode_json:
            return self.get_connection(**kwargs).json()
        else:
            return self.get_connection(**kwargs)

    def post_rule(self, **kwargs):
        kwargs = {'rules': [kwargs]}
        return self.post_connection(**kwargs)

    def delete_rule(self, **kwargs):
        kwargs = {'rules': [kwargs]}
        return self.delete_connection(**kwargs)
