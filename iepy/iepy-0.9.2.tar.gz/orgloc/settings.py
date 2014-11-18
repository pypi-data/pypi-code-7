"""
Django settings for webui project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from iepy.webui.webui.settings import *

IEPY_VERSION = '0.9.1'
SECRET_KEY = 'ls%5dupd+fqltsim*m1=_ml@1(l+7252yl^raniozp3!azmn@s'
DEBUG = False
ALLOWED_HOSTS = ['*']
TEMPLATE_DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "orgloc_clean_small",  # "girls_orgloc_oct_15",
        "USER": "jmansilla",
        "PASSWORD": "montoto"
    }
}
IEPY_VERSION = '0.9.2'  # Remove line declaring the old IEPY_VERSION above.
