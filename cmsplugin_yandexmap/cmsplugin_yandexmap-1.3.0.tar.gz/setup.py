import os
import sys
# hack for utf8 long_description support
reload(sys).setdefaultencoding("UTF-8")
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version='1.3.0'

setup(
    name = 'cmsplugin_yandexmap',
    version = version,
    author = 'Vitaliy Shishorin',
    author_email = 'moskrc@gmail.com',
    url = 'http://bitbucket.org/moskrc/cmsplugin_yandexmap/',
    download_url = 'http://bitbucket.org/moskrc/cmsplugin_yandexmap/get/tip.zip',

    description = 'Plugin for django-cms. Yandex Map.',
    long_description = open('README.rst').read().decode('utf8'),
    license = 'MIT license',
    requires = ['django (>=1.5)','django_cms (>=3.0)'],

    packages=find_packages(),
    package_data={'cmsplugin_yandexmap': ['templates/cmsplugin_yandexmap/*']},


    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    include_package_data=True,
    zip_safe = False,
    install_requires=['django-cms>=2.1.2',],
)
