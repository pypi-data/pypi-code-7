# -*- encoding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig


class DBMailConfig(AppConfig):
    name = 'robokassa'
    verbose_name = _(u'Робокасса')
