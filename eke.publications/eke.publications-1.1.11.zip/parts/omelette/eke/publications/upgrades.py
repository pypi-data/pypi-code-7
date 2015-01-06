# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from Products.CMFCore.utils import getToolByName
from eke.publications.interfaces import IPublicationFolder
from utils import setFacetedNavigation
from eke.publications import PROFILE_ID
import plone.api

def _getPortal(context):
    return getToolByName(context, 'portal_url').getPortalObject()

def nullUpgradeStep(setupTool):
    '''A null step for when a profile upgrade requires no custom activity.'''

def setUpFacetedNavigation(setupTool):
    '''Set up faceted navigation on all Publication Folders.'''
    portal = _getPortal(setupTool)
    request = portal.REQUEST
    catalog = getToolByName(portal, 'portal_catalog')
    results = [i.getObject() for i in catalog(object_provides=IPublicationFolder.__identifier__)]
    if len(results) == 0:
        # wtf? catalog must be out of date, because the common situation is that our EDRN
        # public portal does indeed have at least one Publication Folder
        if 'publications' in portal.keys():
            results = [portal['publications']]
    for pubFolder in results:
        setFacetedNavigation(pubFolder, request)

def runCatalogImportStep(setupTool):
    u'''(Re)Run the portal_catalog GenericSetup import step.'''
    setupTool.runImportStepFromProfile(PROFILE_ID, 'catalog')

def dropExistingPublications(setupTool):
    u'''Drop all existing publications so we can re-create them on the next RDF ingest
    with proper PubMed-provided metadata.'''
    catalog = plone.api.portal.get_tool('portal_catalog')
    results = [i.getObject() for i in catalog(object_provides=IPublicationFolder.__identifier__)]
    if len(results) == 0:
        # wtf? catalog must be out of date, because the common situation is that our EDRN
        # public portal does indeed have at least one Publication Folder
        portal = plone.api.portal.get()
        if 'publications' in portal.keys():
            results = [portal['publications']]
    for pubFolder in results:
        pubFolder.manage_delObjects(pubFolder.objectIds())
