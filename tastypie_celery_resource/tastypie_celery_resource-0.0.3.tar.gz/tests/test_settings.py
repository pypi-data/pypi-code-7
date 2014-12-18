DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ":memory",
    }
}

MIDDLEWARE_CLASSES = ['django.contrib.sessions.middleware.SessionMiddleware']
INSTALLED_APPS = ['django.contrib.sessions']

SECRET_KEY="nonempty"
SESSION_COOKIE_NAME="foobar"

ROOT_URLCONF="tests.test_urls"