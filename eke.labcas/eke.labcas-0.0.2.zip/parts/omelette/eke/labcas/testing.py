# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from plone.app.testing import PloneSandboxLayer, IntegrationTesting, FunctionalTesting, PLONE_FIXTURE
from Products.CMFCore.utils import getToolByName
from eke.labcas import PACKAGE_NAME
import pkg_resources, urllib2, urllib, httplib

class TestSchemeHandler(urllib2.BaseHandler):
    u'''A special URL handler for the testing-only scheme ``testscheme``.'''
    def testscheme_open(self, req):
        try:
            selector = req.get_selector()
            path = 'tests/data/' + selector.split('/')[-1] + '.rdf'
            if pkg_resources.resource_exists(PACKAGE_NAME, path):
                return urllib.addinfourl(
                    pkg_resources.resource_stream(PACKAGE_NAME, path),
                    httplib.HTTPMessage(open('/dev/null')),
                    req.get_full_url(),
                    200
                )
            else:
                raise urllib2.URLError('Not found')
        except Exception:
            raise urllib2.URLError('Not found')


class EKELabCASLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)
    def setUpZope(self, app, configurationContext):
        import eke.labcas
        self.loadZCML(package=eke.labcas)
        urllib2.install_opener(urllib2.build_opener(TestSchemeHandler))
    def setUpPloneSite(self, portal):
        wfTool = getToolByName(portal, 'portal_workflow')
        wfTool.setDefaultChain('plone_workflow')
        self.applyProfile(portal, 'eke.labcas:default')
    
EKE_LABCAS = EKELabCASLayer()
EKE_LABCAS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EKE_LABCAS,),
    name='EKELabCASLayer:Integration'
)
EKE_LABCAS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EKE_LABCAS,),
    name='EKELabCASLayer:Functional'
)
