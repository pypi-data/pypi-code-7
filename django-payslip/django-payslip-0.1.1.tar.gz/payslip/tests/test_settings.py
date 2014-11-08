"""Settings that need to be set in order to run the tests."""
import logging
import os


logging.getLogger("factory").setLevel(logging.WARN)

DEBUG = True

SITE_ID = 1

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

ROOT_URLCONF = 'payslip.tests.urls'

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(__file__, '../../static/')

STATICFILES_DIRS = (
    os.path.join(__file__, 'test_static'),
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), '../templates'),
)

COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), 'coverage')

COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$', 'django_extensions',
]

EXTERNAL_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django_libs',
]

INTERNAL_APPS = [
    'payslip.tests.test_app',
    'payslip',
]

INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS

COVERAGE_MODULE_EXCLUDES += EXTERNAL_APPS

SECRET_KEY = 'foobar'

# Payslip settings
PAYSLIP_CURRENCY = 'SGD'
