"""Test cases for zinnia-markitup"""
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.admin.sites import AdminSite
from django.test.utils import restore_template_loaders
from django.test.utils import setup_test_template_loader

from zinnia.models.entry import Entry
from zinnia.settings import MARKUP_LANGUAGE
from zinnia.signals import disconnect_entry_signals

from zinnia_markitup.admin import EntryAdminMarkItUp


class BaseAdminTestCase(TestCase):

    def setUp(self):
        disconnect_entry_signals()
        self.site = AdminSite()
        self.admin = EntryAdminMarkItUp(
            Entry, self.site)

    def tearDown(self):
        try:
            restore_template_loaders()
        except AttributeError:
            pass


class EntryAdminMarkItUpTestCase(BaseAdminTestCase):
    """Test case for Entry Admin with MarkItUp"""

    def setUp(self):
        super(EntryAdminMarkItUpTestCase, self).setUp()
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get('/')

    def test_markitup(self):
        template_to_use = 'admin/zinnia/entry/markitup.js'
        setup_test_template_loader({template_to_use: ''})
        response = self.admin.markitup(self.request)
        self.assertTemplateUsed(response, template_to_use)
        self.assertEqual(response['Content-Type'], 'application/javascript')

    def test_content_preview(self):
        template_to_use = 'admin/zinnia/entry/preview.html'
        request = self.request_factory.post('/', {'data': 'Hello world'})
        setup_test_template_loader({template_to_use: ''})
        response = self.admin.content_preview(request)
        self.assertTemplateUsed(response, template_to_use)
        self.assertEqual(response.context_data['preview'],
                         '<p>Hello world</p>\n')
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    def test_medias(self):
        medias = self.admin.media
        self.assertEqual(
            medias._css,
            {'all': [
                '/static/zinnia_markitup/js/markitup/skins/django/style.css',
                '/static/zinnia_markitup/js/markitup/sets/%s/style.css' %
                MARKUP_LANGUAGE]})
        self.maxDiff = None
        self.assertEqual(
            medias._js,
            ['/static/admin/js/core.js',
             '/static/admin/js/admin/RelatedObjectLookups.js',
             '/static/admin/js/jquery.min.js',
             '/static/admin/js/jquery.init.js',
             '/static/admin/js/actions.min.js',
             '/static/admin/js/urlify.js',
             '/static/admin/js/prepopulate.min.js',
             '/static/zinnia_markitup/js/jquery.min.js',
             '/static/zinnia_markitup/js/markitup/jquery.markitup.js',
             '/static/zinnia_markitup/js/markitup/sets/'
             'restructuredtext/set.js',
             '/admin/zinnia/entry/markitup/'])
