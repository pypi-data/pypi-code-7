"""
For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from iepy.webui.webui.settings import *

IEPY_VERSION = '0.9.2'
SECRET_KEY = '@=v^m5qo_e2o)rszg)k@*pm$yrttv+v)84mdw&!ormcu*^vgp4'
DEBUG = True
TEMPLATE_DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/jmansilla/projects/iepy/repo/algo/algo.sqlite',
    }
}
