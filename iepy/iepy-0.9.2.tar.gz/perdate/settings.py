"""
Django settings for webui project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from iepy.webui.webui.settings import *

IEPY_VERSION = '0.9.1'
SECRET_KEY = 'sqv*=+av_f9=@g0ye-hvtww@(4t$bg(or&iie9y+v_p_%f_j#!'
DEBUG = True
ALLOWED_HOSTS = ['*']
TEMPLATE_DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "girls_perdate_oct_15",
        "USER": "jmansilla",
        "PASSWORD": "montoto"
    }
}
IEPY_VERSION = '0.9.2'  # Remove line declaring the old IEPY_VERSION above.
