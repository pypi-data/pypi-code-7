# -*- coding: utf-8 -*-
"""Setup handlers for plone.mls.listing."""

# zope imports
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import getUtility

LISTING_TYPE = 'plone.mls.listing.listing'


def setup_article(context):
    """Set up raptus.article."""
    if not context.readDataFile('plone.mls.listing_various.txt'):
        return

    site = getUtility(IPloneSiteRoot)
    quickinstaller = getToolByName(site, 'portal_quickinstaller')
    portal_types = getToolByName(site, 'portal_types')
    if quickinstaller.isProductInstalled('raptus.article.core'):
        article = portal_types.get('Article', None)
        if article is None:
            return
        if LISTING_TYPE not in article.allowed_content_types:
            article.allowed_content_types += (LISTING_TYPE, )
