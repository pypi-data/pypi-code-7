# -*- coding: utf-8 -*-
from flask import request


class   LazyText(object):
    def __init__(self, singular, plural=None, n=0):
        self.__s = singular
        self.__p = plural
        self.__n = n
        self.__d = None

    def __unicode__(self):
        if self.__p is None:
            return request.__dict__['i18n_engine'].ugettext(self.__s)
        return request.__dict__['i18n_engine'].ungettext(self.__s, self.__p, self.__n)

    def __str__(self):
        try:
            return self.__unicode__()
        except RuntimeError:
            return self.__s

    def __mod__(self, other):
        s = self.__unicode__()
        return s % other

    def __call__(self, other = None):
        if other is None:
            return self.__unicode__()
        s = self.__unicode__()
        return s % other
