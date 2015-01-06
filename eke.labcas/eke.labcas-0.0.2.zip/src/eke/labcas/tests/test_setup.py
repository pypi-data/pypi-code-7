# encoding: utf-8
#
# Copyright 2013 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''LabCAS for EKE — setup tests'''

from eke.labcas.testing import EKE_LABCAS_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
import unittest2 as unittest

class SetupTest(unittest.TestCase):
    layer = EKE_LABCAS_INTEGRATION_TESTING
    def setUp(self):
        super(SetupTest, self).setUp()
        self.portal = self.layer['portal']
    def testTypes(self):
        u'''Check types'''
        types = getToolByName(self.portal, 'portal_types')
        for t in ('eke.labcas.labcasfolder', 'eke.labcas.labcasdataset'):
            self.failUnless(t in types, u'Type {} not in portal_types'.format(t))
        folderType = types['eke.labcas.labcasfolder']
        self.failUnless('eke.labcas.labcasdataset' in folderType.allowed_content_types,
            u"eke.labcas.labcasdataset doesn't appear in eke.labcas.labcasfolder's allowed types")
