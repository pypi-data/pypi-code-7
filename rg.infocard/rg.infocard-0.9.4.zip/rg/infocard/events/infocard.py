# -*- coding: utf-8 -*-
from BTrees.OOBTree import OOTreeSet
from .. import rg_infocard_logger as logger
from plone import api


def register_infocard_authors(obj):
    """@param obj: an infocard
    """
    infocard_authors = getattr(obj, 'infocard_authors', OOTreeSet())
    try:
        user = api.user.get_current()
        infocard_authors.add(user.fullname or user.getId())
    except:
        msg = "problem getting author"
        logger.exception(msg)
    obj.infocard_authors = infocard_authors


def modified(obj, event):
    """
    @param obj: an infocard
    @param event: Subclass of event.
    """
    register_infocard_authors(obj)
