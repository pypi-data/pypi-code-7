# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='thorium_htmlpurifier',
    description='HTML Purifier validation for Thorium',
    packages=['thorium_htmlpurifier'],
    version='0.1.1',
    author='Devon Meunier',
    author_email='devon@eventmobi.com',
    url='https://github.com/meunierd/thorium_htmlpurifier/',
    zip_safe=False,
    install_requires=[
        'coverage',
        'html-purifier3>=2.1.0',
        'nose',
        'thorium',
    ],
    test_suite='nose.collector',
)
