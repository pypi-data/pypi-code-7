from common import *




DEBUG = False
ALLOWED_HOSTS = ['*',]
TEMPLATE_DEBUG = DEBUG
MODO_SERVIDOR = 'PROD'

DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'endless_pagination',
    'autocomplete_light',
)
# Combine all the apps in the django variable INSTALLED_APPS
from  django_microsip_base.settings.local_settings import EXTRA_APPS
from  django_microsip_base.settings.local_settings import MICROSIP_VERSION

MICROSIP_EXTRA_APPS = ()
for microsip_app in EXTRA_APPS:
    MICROSIP_EXTRA_APPS += (microsip_app['app'],)
    
INSTALLED_APPS = DJANGO_APPS + MICROSIP_MODULES + MICROSIP_EXTRA_APPS

ROOT_URLCONF = 'django_microsip_base.urls.prod'

# Additional locations of static files
STATICFILES_DIRS = (
    (BASE_DIR + '/static/'),
)