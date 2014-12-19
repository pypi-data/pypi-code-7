# -*- coding: utf-8 -*-
"""Init and utils."""
from logging import getLogger
from zope.i18nmessageid import MessageFactory

PRODUCT_ID = 'rg.infocard'

rg_infocard_msgfactory = MessageFactory(PRODUCT_ID)
rg_infocard_logger = getLogger(PRODUCT_ID)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
