# -*- coding: utf-8 -*-

__author__ = "Nikolay Dolganov"
__email__ = "SirNikolasd@yandex.ru"

from cms.test_utils.testcases import CMSTestCase
from django.http import HttpRequest
from cms.admin.forms import PageForm
from django.conf import settings
from cms.models.titlemodels import Title
from ..models import Metadata


class TestPageTitles(CMSTestCase):
    """
    Test Custom page titles
    """

    def setUp(self):
        # Create superuser
        self.superuser = self.get_superuser()

    def __create_page(self, page_data, without_h1=False):
        """
        Creates page with h1 or without it
        :param page_data: dict
        :return Page
        """
        if not without_h1:
            page_data["title"] = "Page with titles and META"
            page_data["slug"] = "page-with-data-and-meta"
        # rewrite template name
        page_data['template'] = settings.CMS_TEMPLATES[0][0]
        # Save page
        self.page_form = PageForm(page_data)
        self.assertTrue(self.page_form.is_valid())
        page = self.page_form.save(commit=False)
        return page

    def __extend_page(self, page, page_data):
        """
        Creates Title and Meta Extension for given page
        :param page: Page
        :param page_data: dict
        """
        # Get Request
        request = HttpRequest()
        request.user = self.superuser
        # Get Title Object
        title = Title.objects.set_or_create(request, page, self.page_form, settings.LANGUAGE_CODE)
        # Extend page
        ext = Metadata(extended_object=title, h1='H1 is ready to use')
        ext.save()

    def test_titles_and_meta(self):
        """
        Test H1 attribute
        """
        from django import template

        with self.login_user_context(self.superuser):

            # Create pages
            page_data = self.get_new_page_data()
            pages = {
                'page_with': self.__create_page(page_data),
                'page_without': self.__create_page(page_data, without_h1=True)
            }

            # Create template
            t = template.Template(
                "{% load cms_tags %}Page: {{ request.current_page.get_title_obj.metadata.h1 }}")

            # Post pages on the site
            for page_type, page in pages.items():
                page.save()
                # If page must to be with extra Titles and META data
                if page_type == 'page_with':
                    self.__extend_page(page, page_data)
                    page.publish(settings.LANGUAGE_CODE)

            # Test page without h1
            req = HttpRequest()
            req.current_page = pages['page_without']
            req.REQUEST = {}
            rendered = t.render(template.Context({"request": req}))
            self.assertEqual(rendered, "Page: ")

            # Test page with h1
            req = HttpRequest()
            req.current_page = pages['page_with']
            req.REQUEST = {}
            rendered = '{0}'.format(t.render(template.Context({"request": req})))
            self.assertEqual(rendered, "Page: H1 is ready to use")