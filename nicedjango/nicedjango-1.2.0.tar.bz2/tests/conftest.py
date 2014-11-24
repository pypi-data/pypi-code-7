def pytest_configure():
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        # DATABASE_ENGINE='django.db.backends.mysql',
        # DATABASES={'default': {'ENGINE': 'django.db.backends.mysql',
        #                       'NAME': 'momox', 'HOST': '127.0.0.1', 'USER': 'root',
        #                       'OPTIONS': {'init_command': 'SET storage_engine=INNODB; SET character_set_database=UTF8;',
        #                                   'local_infile': 1},
        #                      }},
        DATABASE_ENGINE='django.db.backends.sqlite3',
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3',
                               'NAME': ':memory:'}},
        SITE_ID=1,
        SECRET_KEY='not very secret in tests',
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        ROOT_URLCONF='tests.urls',
        TEMPLATE_LOADERS=(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ),
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',

            'nicedjango',
            'tests',
            'tests.a1',
            'tests.a2',
            'tests.a3',
        ),
        LOGGING={'version': 1,
                 'handlers': {
                     'console': {
                         'level': 'DEBUG',
                         'class': 'logging.StreamHandler', }, },
                 'loggers': {'django.db.backends': {'level': 'DEBUG', 'handlers': ['console']}}},
        DEBUG=True,
    )
    import django
    if hasattr(django, 'setup'):
        django.setup()
    import logging
    logging.basicConfig(level=logging.DEBUG)
    for level, color_code in ((logging.INFO, 32), (logging.WARNING, 33),
                              (logging.ERROR, 31), (logging.DEBUG, 34),
                              (logging.CRITICAL, 35)):
        logging.addLevelName(level, "\033[1;%dm%s\033[1;m"
                             % (color_code, logging.getLevelName(level)))
