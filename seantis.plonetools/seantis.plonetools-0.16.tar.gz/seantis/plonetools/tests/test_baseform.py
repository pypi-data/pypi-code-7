from plone import api

from seantis.plonetools import tests
from seantis.plonetools.browser import BaseForm


class TestBaseForm(tests.IntegrationTestCase):

    def test_urls(self):

        form = BaseForm(api.portal.get(), self.request)

        self.assertEqual(form.success_url, 'http://nohost/plone')
        self.assertEqual(form.cancel_url, 'http://nohost/plone')

    def test_translate(self):

        form = BaseForm(api.portal.get(), self.request)

        self.assertRaises(NotImplementedError, form.translate, u'')
        self.assertEqual(form.translate(u'Yes', domain='plone'), u'Yes')

    def test_buttons(self):

        form = BaseForm(api.portal.get(), self.request)
        form.update()

        self.assertEqual(len(form.buttons), 2)
        self.assertEqual(len(form.handlers._handlers), 2)

        self.assertIn('context', form.actions['save'].klass)
