# -*- coding: utf-8 -*-

import os
import pickle

from django.core.cache import cache

from grab import spider, response, Grab as GrabLib

import defaults
import models


APP_ROOT = os.path.normpath(os.path.dirname(__file__))
PC_USER_AGENT_FILE = os.path.join(APP_ROOT, 'data/pc_agents.txt')
MOBILE_USER_AGENT_FILE = os.path.join(APP_ROOT, 'data/mobile_agents.txt')


class ActiveProxiesNotFound(Exception):
    """
    Raised when active proxies not found on database
    """


def get_db_proxies(db_cache_ttl=10, grabber_cache_key='grabber_proxies_list'):
    cached = cache.get(grabber_cache_key)
    if cached:
        return cached

    proxies_list = models.Proxy.objects.values(
        'hostname', 'port', 'user', 'password'
    ).filter(errors=0, last_check__isnull=False)
    if defaults.PROXY_MIN_ANONYMITY_LEVEL:
        proxies_list = proxies_list.filter(
            anonymity_level__gte=defaults.PROXY_MIN_ANONYMITY_LEVEL
        )

    if not proxies_list.exists():
        raise ActiveProxiesNotFound

    proxies = []
    for obj in proxies_list:
        proxy = '%s:%d' % (obj['hostname'], obj['port'])
        if obj['user'] and obj['password']:
            proxy += ':%s:%s' % (obj['user'], obj['password'])
        proxies.append(proxy)
    cache.set(grabber_cache_key, proxies, db_cache_ttl)
    return proxies


def get_default_settings(mobile_devices=False):
    user_agent_file = PC_USER_AGENT_FILE
    if mobile_devices is True:
        user_agent_file = MOBILE_USER_AGENT_FILE
    return {
        'user_agent_file': user_agent_file,
        'connect_timeout': defaults.GRABBER_CONNECT_TIMEOUT,
        'timeout': defaults.GRABBER_TIMEOUT,
        'hammer_mode': True,
        'hammer_timeouts': defaults.GRABBER_HAMMER_TIMEOUTS,
        'headers': defaults.GRABBER_HEADERS
    }


class Grab(GrabLib):
    response_keys = (
        'status', 'code', 'head', 'body', 'total_time',
        'connect_time', 'name_lookup_time',
        'url', 'charset', '_unicode_body'
    )

    def __init__(self, *args, **kwargs):
        mobile_device = kwargs.pop('mobile_devices', False)
        use_proxy = kwargs.pop('use_db_proxy', True)
        db_cache_ttl = kwargs.pop(
            'db_cache_ttl', defaults.PROXY_LIST_DB_CACHE_TTL)

        default_settings = get_default_settings(mobile_device)
        default_settings.update(kwargs)

        super(Grab, self).__init__(*args, **default_settings)

        if use_proxy is True:
            self.load_proxylist(
                source=get_db_proxies(db_cache_ttl),
                source_type='list',
                auto_init=True,
                auto_change=kwargs.get('proxy_auto_change', True)
            )

    def dump_current_session(self):
        if self.response:
            data = {'config': self.dump_config(), 'response': {}}
            for key in self.clonable_attributes:
                data[key] = getattr(self, key)

            data['response']['headers'] = self.response.headers
            data['response']['cookies'] = self.response.cookies

            for key in self.response_keys:
                data['response'][key] = getattr(self.response, key)

            return pickle.dumps(data)

    def load_previous_session(self, session):
        session = pickle.loads(session)
        _response = session.pop('response')
        self.response = response.Response()

        for k, v in session.items():
            setattr(self, k, v)

        for k, v in _response.items():
            setattr(self.response, k, v)


class Spider(spider.base.Spider):
    def create_grab_instance(self):
        return Grab(**self.grab_config)
