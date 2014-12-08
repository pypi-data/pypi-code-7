import django.core.exceptions

from django.conf import settings

try:
    getattr(settings, '')
except django.core.exceptions.ImproperlyConfigured:
    settings = {}

REDIS = {
    'password': '',
    'port': 6379,
    'host': 'localhost',
}
if hasattr(settings, 'REDIS'):
    REDIS.update(settings.REDIS)

HOME_URL = getattr(settings, 'HOME_URL', '/')
PRIMARY_USER_MODEL = getattr(settings, 'PRIMARY_USER_MODEL', 'app.User')

