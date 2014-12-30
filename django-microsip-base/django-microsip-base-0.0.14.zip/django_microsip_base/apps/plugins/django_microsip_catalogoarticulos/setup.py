import os
from setuptools import setup

# README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django_microsip_catalogoarticulos',
    version = '0.0.1',
    packages = ['django_microsip_catalogoarticulos'],
    include_package_data = True,
    license = 'BSD License', # example license
    description = 'django_microsip_catalogoarticulos',
    long_description = 'README',
    url = '',
    author = 'Servicios de Ingenieria Computacional',
    author_email = 'jesusmahererra@gmail.com',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
