# -*- coding: utf-8 -*-

from django.conf import settings


def get_settings(key, default):
    return getattr(settings, key, default)


PROXY_LIST_CACHE_TIMEOUT = get_settings(
    "PROXY_LIST_CACHE_TIMEOUT", 0)
PROXY_LIST_CONNECTION_TIMEOUT = get_settings(
    "PROXY_LIST_CONNECTION_TIMEOUT", 10)
PROXY_LIST_ERROR_DELAY = get_settings(
    "PROXY_LIST_ERRORDELAY", 300)
PROXY_LIST_GEOIP_PATH = get_settings(
    "PROXY_LIST_GEOIP_PATH", "/usr/share/GeoIP/GeoIP.dat")
PROXY_LIST_MAX_CHECK_INTERVAL = get_settings(
    "PROXY_LIST_MAX_CHECK_INTERVAL", 900)
PROXY_LIST_MIN_CHECK_INTERVAL = get_settings(
    "PROXY_LIST_MIN_CHECK_INTERVAL", 300)
PROXY_LIST_OUTIP_INTERVAL = get_settings(
    "PROXY_LIST_OUTIP_INTERVAL", 3600)
PROXY_LIST_USER_AGENT = get_settings(
    "PROXY_LIST_USER_AGENT", "Django-Proxy 1.0.0")
PROXY_LIST_ELAPSED_TIME = get_settings('PROXY_LIST_ELAPSED_TIME', None)
PROXY_CHECK_RESULTS = get_settings('PROXY_CHECK_RESULTS', False)

if 'djcelery' not in settings.INSTALLED_APPS:
    PROXY_LIST_USE_CELERY = False
else:
    PROXY_LIST_USE_CELERY = get_settings("PROXY_LIST_USE_CELERY", False)

GRABBER_HEADERS = get_settings(
    'GRABBER_HEADERS', {'Accept-Language': 'ru-ru,ru;q=0.7'})
GRABBER_HAMMER_TIMEOUTS = get_settings(
    'GRABBER_HAMMER_TIMEOUTS', ((60, 70), (80, 90), (100, 110)))
GRABBER_TIMEOUT = get_settings('GRABBER_TIMEOUT', 60)
GRABBER_CONNECT_TIMEOUT = get_settings('GRABBER_CONNECT_TIMEOUT', 2)
PROXY_LIST_DB_CACHE_TTL = get_settings('PROXY_LIST_DB_CACHE_TTL', 10)

SPIDER_PAGE_END = get_settings('SPIDER_PAGE_END', 2)

ADMIN_BUTTONS = get_settings('PROXY_ADMIN_BUTTONS', [
    'Clean', 'Check', 'Grab'
])

PROXY_MIN_ANONYMITY_LEVEL = get_settings('PROXY_MIN_ANONYMITY_LEVEL', None)
CALCULATE_ELAPSED_TIME_REQUESTS_RANGE = get_settings(
    'PROXY_CALCULATE_ELAPSED_TIME_REQUESTS_RANGE', range(2, 6))
