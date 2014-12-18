from local_settings import *
from common import *
import os
import fdb
import sqlite3
DATABASE_ROUTERS = ['django_microsip_base.libs.databases_routers_test.MainRouter']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME':  os.path.join(BASE_DIR, 'data' ,'USERS.sqlite3'),
        'TEST_NAME': os.path.join(BASE_DIR, 'data' ,'test_USERS.sqlite3'),
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'ATOMIC_REQUESTS': True,
    },
   'CONFIG' :{
        'ENGINE': 'django.db.backends.firebird', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'C:\Microsip datos\System\CONFIG.FDB',
        'USER': 'SYSDBA',                      # Not used with sqlite3.
        'PASSWORD': 'masterkey',                  # Not used with sqlite3.
        'HOST': 'localhost',
        'TEST_NAME':'C:\Microsip datos\System\\test_CONFIG.FDB',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3050',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS' : {'charset':'ISO8859_1'},
        'ATOMIC_REQUESTS': True,
    },
	'AD2007' :{
	    'ENGINE': 'django.db.backends.firebird', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
	    'NAME': 'C:\Microsip datos\AD2007.FDB',
	    'USER': 'SYSDBA',                      # Not used with sqlite3.
	    'PASSWORD': 'masterkey',                  # Not used with sqlite3.
	    'HOST': 'localhost',      
        'TEST_NAME':'C:\Microsip datos\\test_AD2007.FDB',                # Set to empty string for localhost. Not used with sqlite3.
	    'PORT': '3050',                      # Set to empty string for default. Not used with sqlite3.
	    'OPTIONS' : {'charset':'ISO8859_1'},
	    'ATOMIC_REQUESTS': True,
	}

}