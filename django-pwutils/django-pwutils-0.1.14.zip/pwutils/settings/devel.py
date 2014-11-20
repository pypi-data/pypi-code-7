
import os

from .base import *

DEBUG = True
TEMPLATE_DEBUG = True
THUMBNAIL_DUMMY = True

# remove cached loader from template loaders
try:
    if 'cached.Loader' in TEMPLATE_LOADERS[0][0]:
        TEMPLATE_LOADERS = TEMPLATE_LOADERS[0][1]
except IndexError:
    pass

INSTALLED_APPS = INSTALLED_APPS + (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(PROJECT_ROOT, 'messages')

DEBUG_TOOLBAR_PANELS = (
  'debug_toolbar.panels.versions.VersionsPanel',
  'debug_toolbar.panels.timer.TimerPanel',
  'debug_toolbar.panels.settings.SettingsPanel',
  'debug_toolbar.panels.headers.HeadersPanel',
  'debug_toolbar.panels.request.RequestPanel',
  'debug_toolbar.panels.templates.TemplatesPanel',
  'debug_toolbar.panels.staticfiles.StaticFilesPanel',
  'debug_toolbar.panels.sql.SQLPanel',
  'debug_toolbar.panels.signals.SignalsPanel',
  'debug_toolbar.panels.logging.LoggingPanel',
  'debug_toolbar.panels.cache.CachePanel',
  'debug_toolbar.panels.redirects.RedirectsPanel',
  'debug_toolbar.panels.profiling.ProfilingPanel',
)

DEBUG_TOOLBAR_CONFIG = {
#    'ENABLE_STACKTRACES': True,
    'INTERCEPT_REDIRECTS': False,
}

# For sql_queries
INTERNAL_IPS = (
    "127.0.0.1",
)

import copy
from django.utils.log import DEFAULT_LOGGING
LOGGING = copy.deepcopy(DEFAULT_LOGGING)

LOGGING.setdefault('formatters', {})
LOGGING['formatters']['adv'] = {
      'format': '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    }
LOGGING['handlers']['console']['formatter'] = 'adv'

LOGGING['handlers']['console_dev'] = LOGGING['handlers']['console'].copy()
LOGGING['handlers']['console_dev']['level'] = 'DEBUG'

LOGGING['loggers'][''] = {
      'handlers': ['console'],
      'level': 'DEBUG',
    }

for logger in locals().get('DEBUG_LOGGERS', []):
    LOGGING['loggers'][logger] = {'handlers': ['console_dev'], 
                                  'level':'DEBUG',
                                  'propagate': False}

# drop printing HTTP messages for static
from django.core.servers.basehttp import WSGIRequestHandler

def new_log_message(self, format, *args):
    if self.path.startswith('/static'):
        return
    return self._old_log_message(format, *args)

WSGIRequestHandler._old_log_message = WSGIRequestHandler.log_message
WSGIRequestHandler.log_message = new_log_message
