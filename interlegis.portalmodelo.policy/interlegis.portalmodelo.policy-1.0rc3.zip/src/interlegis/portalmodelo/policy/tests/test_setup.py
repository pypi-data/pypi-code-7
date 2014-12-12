# -*- coding: utf-8 -*-
from interlegis.portalmodelo.policy.config import PROFILE_ID
from interlegis.portalmodelo.policy.config import PROJECTNAME
from interlegis.portalmodelo.policy.testing import INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest

# these packages must be available, but not installed
AVAILABLE = [
    'brasil.gov.vcge',
    'interlegis.intranetmodelo.policy',
    'webcouturier.dropdownmenu',
]

DEPENDENCIES = [
    'collective.cover',
    'collective.flowplayer',
    'collective.polls',
    'collective.upload',
    'EasyNewsletter',
    'interlegis.portalmodelo.api',
    'interlegis.portalmodelo.buscadores',
    'interlegis.portalmodelo.ombudsman',
    'interlegis.portalmodelo.pl',
    'interlegis.portalmodelo.theme',
    'plone.app.event',
    'Ploneboard',
    'PloneFormGen',
    'sc.blog',
    'sc.embedder',
    'sc.galleria.support',
    'sc.social.like',
    'Solgema.fullcalendar',
    'windowZ',
]


class InstallTestCase(unittest.TestCase):
    """Ensure package is properly installed."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        self.setup = self.portal['portal_setup']

    def test_installed(self):
        self.assertTrue(self.qi.isProductInstalled(PROJECTNAME))

    def test_dependencies_installed(self):
        for i in DEPENDENCIES:
            self.assertTrue(
                self.qi.isProductInstalled(i), u'{0} not installed'.format(i))

    def test_available_packages(self):
        for i in AVAILABLE:
            self.assertIn(i, self.qi.listInstallableProfiles())

    def test_mailtogroup_content_rule_registered(self):
        from plone.contentrules.rule.interfaces import IRuleAction
        from zope.component import queryUtility
        rule = queryUtility(IRuleAction, name='plone.actions.MailGroup')
        self.assertIsNotNone(rule)

    def test_version(self):
        self.assertEqual(
            self.setup.getLastVersionForProfile(PROFILE_ID), (u'1',))


class DependenciesSettingsTestCase(unittest.TestCase):
    """Ensure package dependencies are properly configured."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.registry = getUtility(IRegistry)

    def test_collective_cover_settings(self):
        from collective.cover.controlpanel import ICoverSettings
        settings = self.registry.forInterface(ICoverSettings)
        self.assertEqual(len(settings.layouts), 1)
        self.assertIn(u'Portal Modelo', settings.layouts)

    def test_collective_upload_settings(self):
        from collective.upload.interfaces import IUploadSettings
        settings = self.registry.forInterface(IUploadSettings)
        expected = 'gif, jpeg, jpg, png, pdf, doc, txt, docx, ods, odt, odp, html, csv, zip, tgz, ppt, pptx, xls, xlsx'
        self.assertEqual(settings.upload_extensions, expected)
        self.assertEqual(settings.max_file_size, 10485760)
        self.assertEqual(settings.resize_max_width, 3872)
        self.assertEqual(settings.resize_max_height, 3872)

    def test_plone_app_event_settings(self):
        self.assertEqual(
            self.registry['plone.app.event.portal_timezone'], u'Brazil/East')
        self.assertListEqual(
            self.registry['plone.app.event.available_timezones'],
            [u'Brazil/Acre', u'Brazil/DeNoronha', u'Brazil/East', u'Brazil/West']
        )
        self.assertEqual(self.registry['plone.app.event.first_weekday'], u'6')

