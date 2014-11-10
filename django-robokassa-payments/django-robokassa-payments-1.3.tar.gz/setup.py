# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages
from robokassa import get_version


setup(
    name='django-robokassa-payments',
    version=get_version(),
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',
    maintainer='gotlium',
    maintainer_email='gotlium@gmail.com',
    packages=find_packages(exclude=['demo']),
    include_package_data=True,
    url='https://github.com/LPgenerator/django-robokassa/',
    license='MIT license',
    description=u'Приложение для интеграции платежной системы '
                u'ROBOKASSA в проекты на Django.'.encode('utf8'),
    long_description=open('README.rst').read().decode('utf8'),
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Russian',
    ),
)
