# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from cStringIO import StringIO


def runProfile(portal, profileName):
    setupTool = getToolByName(portal, 'portal_setup')
    setupTool.runAllImportStepsFromProfile(profileName)


def install(portal):
    """Run the GS profile to install this package"""
    out = StringIO()
    runProfile(portal, 'profile-collective.pdfpeek:default')
    print >>out, 'Installed collective.pdfpeek'  # noqa
    return out.getvalue()


def beforeUninstall(portal, reinstall, product, cascade):
    try:
        cascade.remove('portalobjects')
    except:
        ValueError
    return None, cascade


def uninstall(portal, reinstall=False):
    """Run the GS profile to install this package"""
    out = StringIO()
    if not reinstall:
        runProfile(portal, 'profile-collective.pdfpeek:uninstall')
        print >>out, 'Uninstalled collective.pdfpeek'  # noqa
    return out.getvalue()
