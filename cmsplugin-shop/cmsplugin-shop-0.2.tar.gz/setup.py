# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
]

package_data = {
    'cmsplugin_shop': [
        'templates/cmsplugin_shop/*',
        'templates/cmsplugin_shop/*/*',
        'locale/*/*/*'
    ],
    'cmsplugin_shop.templatetags': [],
}

setup(
    name         = 'cmsplugin-shop',
    version      = '0.2',
    license      = 'BSD',
    description  = 'Extensible E-Shop plugin for djangoCMS',
    author       = 'Jakub Dorňák',
    author_email = 'jdornak@redhat.com',
    url          = 'https://github.com/misli/cmsplugin-shop',
    packages     = find_packages(),
    package_data = package_data,
    classifiers  = classifiers,
)

