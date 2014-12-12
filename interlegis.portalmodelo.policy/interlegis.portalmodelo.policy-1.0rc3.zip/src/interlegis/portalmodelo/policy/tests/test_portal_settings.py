# -*- coding: utf-8 -*-
from interlegis.portalmodelo.policy.testing import INTEGRATION_TESTING
from plone import api

import unittest


class SitePropertiesTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.properties = self.portal['portal_properties'].site_properties
        self.languages = self.portal['portal_languages']
        self.types = self.portal['portal_types']
        self.maxDiff = None

    def test_title(self):
        self.assertEqual(self.portal.title, 'Portal Modelo')

    def test_description(self):
        self.assertEqual(
            self.portal.description, 'O portal das casas legislativas')

    def test_validate_email_is_enabled(self):
        self.assertTrue(self.portal.validate_email)

    def test_allowAnonymousViewAbout_is_enabled(self):
        self.assertTrue(self.properties.allowAnonymousViewAbout)

    def test_displayPublicationDateInByline_is_enabled(self):
        self.assertTrue(self.properties.displayPublicationDateInByline)

    def test_localTimeFormat(self):
        self.assertEqual(self.properties.localTimeFormat, '%d/%m/%Y')

    def test_localLongTimeFormat(self):
        self.assertEqual(self.properties.localLongTimeFormat, '%d/%m/%Y %H:%M')

    def test_enable_link_integrity_checks_is_enabled(self):
        self.assertTrue(self.properties.enable_link_integrity_checks)

    def test_livesearch_is_enabled(self):
        self.assertTrue(self.properties.enable_livesearch)

    def test_brasilian_portuguese_is_default_language(self):
        self.assertTrue(self.languages.use_combined_language_codes)
        self.assertEqual(self.properties.default_language, 'pt-br')

    def test_utf8_is_default_charset(self):
        self.assertEqual(self.properties.default_charset, 'utf-8')
        self.assertEqual(self.portal.email_charset, 'utf-8')

    def test_types_searched(self):
        all_types = set(self.types.listContentTypes())
        types_not_searched = set(self.properties.types_not_searched)
        types_searched = all_types - types_not_searched
        expected = [
            'Blog',
            'Claim',
            'Collection',
            'collective.polls.poll',
            'CSVData',
            'Document',
            'EasyNewsletter',
            'Event',
            'File',
            'Folder',
            'FormFolder',
            'Image',
            'Legislature',
            'Link',
            'News Item',
            'OmbudsOffice',
            'Parliamentarian',
            'Ploneboard',
            'PloneboardComment',
            'PloneboardForum',
            'sc.embedder',
            'Session',
            'Window',
        ]
        self.assertItemsEqual(types_searched, expected)

    def test_icons_are_visible_to_authenticated_users_only(self):
        self.assertEqual(self.properties.icon_visibility, 'authenticated')


class NavtreePropertiesTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.navtree = self.portal['portal_properties'].navtree_properties
        self.types = self.portal['portal_types']
        self.maxDiff = None

    def test_content_types_displayed_on_navigation(self):
        all_types = set(self.types.listContentTypes())
        metaTypesNotToList = set(self.navtree.metaTypesNotToList)
        content_types_displayed = all_types - metaTypesNotToList
        expected = [
            'Blog',
            'Collection',
            'Document',
            'EasyNewsletter',
            'Folder',
            'FormFolder',
            'Link',
            'OmbudsOffice',
            'Ploneboard',
            'PloneboardForum',
            'Window',
        ]
        self.assertItemsEqual(content_types_displayed, expected)

    def test_ids_not_to_list_on_navigation(self):
        idsNotToList = set(self.navtree.idsNotToList)
        expected = [
            'front-page',
            'footer-page',
        ]
        self.assertItemsEqual(idsNotToList, expected)


class SyndicationPropertiesTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.actions = api.portal.get_tool('portal_actions').document_actions
        self.base_registry = 'Products.CMFPlone.interfaces.syndication.ISiteSyndicationSettings'

    def test_rss_action(self):
        rss_action = self.actions.rss
        self.assertTrue(rss_action.visible)

    def test_syndication_enabled(self):
        record = 'default_enabled'
        enabled = api.portal.get_registry_record(
            '{0}.{1}'.format(self.base_registry, record)
        )
        self.assertTrue(enabled)

    def test_syndication_link(self):
        record = 'show_syndication_link'
        show = api.portal.get_registry_record(
            '{0}.{1}'.format(self.base_registry, record)
        )
        self.assertTrue(show)


class HomePropertiesTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def test_index_action(self):
        self.portal = self.layer['portal']
        self.actions = api.portal.get_tool('portal_actions').portal_tabs
        home_action = self.actions.index_html
        self.assertEqual(home_action.url_expr, 'string:${portal_url}')


class PloneBoardTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.pb = self.portal['portal_ploneboard']

    def test_enable_anon_name(self):
        self.assertTrue(self.pb.enable_anon_name)

