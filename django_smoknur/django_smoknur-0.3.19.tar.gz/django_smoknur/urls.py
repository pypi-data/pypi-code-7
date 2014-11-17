# coding: utf-8

"""
модуль, роутинга урлов и представлений
"""

try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url


def get_urls():
    """
    возвращает роутинг урлов
    """

    return patterns(
        '',
        url(r'smoknur', 'django_smoknur.views.debug')
    )
