# -*- coding: utf-8 -*-
from flask import request, g


def     jinja_get_translation_engine():
    try:
        return getattr(request, 'i18n_engine')
    except:
        return getattr(g, 'i18n_engine', None)
