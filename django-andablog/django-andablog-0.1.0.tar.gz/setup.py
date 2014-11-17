#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('docs/history.rst').read().replace('.. :changelog:', '')

requirements = [
    'six',
    'Django>=1.6',
    'django-model-utils>=2.2',
    'django-markitup>=2.2.2',
    'pillow>=2.6.1',
]

test_requirements = [
    # None, these go into the test_requirements file
]

setup(
    name='django-andablog',
    version='0.1.0',
    description='A blog app that is only intended to be embedded within an existing Django site.',
    long_description=readme + '\n\n' + history,
    author='Ivan VenOsdel',
    author_email='ivan@wimpyanalytics.com',
    url='https://github.com/WimpyAnalytics/django-andablog',
    download_url='https://github.com/wimpyanalytics/django-andablog/tarball/0.1.0',
    packages=[
        'djangoandablog',
    ],
    package_dir={'djangoandablog':
                 'djangoandablog'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords=['django-andablog', 'blog', 'django', 'app', 'reusable app'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
