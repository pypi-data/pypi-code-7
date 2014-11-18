# -*- coding: utf-8 -*-
from .base import SimpleSafeVocabulary, safe_term
from five import grok
from zope.schema.interfaces import IContextSourceBinder


@grok.provider(IContextSourceBinder)
def InfocardServicetypes(context):
    '''
    Get the servicetypes from the parent infocardcontainer

    :param context: a Plone object
    '''
    from rg.infocard.models.infocardcontainer import Infocardcontainer
    for obj in context.aq_chain:
        if isinstance(obj, Infocardcontainer):
            values = set([x.strip() for x in obj.servicetypes if x.strip()])
            values = sorted(values)
            terms = map(safe_term, values)
            return SimpleSafeVocabulary(terms)
    return SimpleSafeVocabulary([])
