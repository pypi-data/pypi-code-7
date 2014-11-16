# -*- coding: utf-8 -*-
from flask import request
from gettext import GNUTranslations, NullTranslations
from locale import setlocale, LC_ALL
from os.path import join
from ...g import settings


def     flask_before_i18n_set_user_language(lng=None):
    # Get current request language
    if lng is None:
        lng = request.headers.get('Accept-Language')
    if lng is not None:
        lng = lng[0:2]  # Todo: check priority : en-US,en;q=0.5
    else:
        lng = 'en'
    setattr(request, 'i18n_language', lng)

    # Init i18n
    try:
        setlocale(LC_ALL, (lng, 'utf-8'))
    except:
        setlocale(LC_ALL, '')

    # Build translation filename
    if lng not in settings.FLASK_TRANSLATION_LNG:
        lng = settings.FLASK_TRANSLATION_LNG[0]
    filename = ''
    filename = join(filename, join(join(settings.FLASK_TRANSLATION_DIR, lng), 'LC_MESSAGES/messages.mo'))

    # Open translation file or use NullTranslation if fail
    try:
        trans = GNUTranslations(open(filename, 'rb'))
    except IOError:
        trans = NullTranslations()

    # Install i18n
    trans.install()
    setattr(request, 'i18n_engine', trans)
