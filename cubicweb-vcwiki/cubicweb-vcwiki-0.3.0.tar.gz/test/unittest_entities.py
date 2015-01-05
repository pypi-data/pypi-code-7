# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-vcwiki entity tests"""


from cubicweb.web.views.ibreadcrumbs import IBreadCrumbsAdapter

from utils import VCWikiTC


class VCWikiContentTC(VCWikiTC):

    def test_simple(self):
        req = self.request()
        self.assertIsNotNone(self.vcwiki.content('hello.rst'))

    def test_directory(self):
        content = self.vcwiki.content('subject1.rst')
        self.assertEqual('index file of subject1 folder\n',
                         content)

    def test_root(self):
        content = self.vcwiki.content('index.rst')
        self.assertEqual('index file of the root folder\n',
                         content)

    def test_does_not_exist(self):
        content = self.vcwiki.content('does_not_exist.rst')
        self.assertIsNone(content)

    def test_deleted(self):
        content = self.vcwiki.content('deleted.rst')
        self.assertIsNone(content)
        content = self.vcwiki.content('deleted.rst', allow_deleted=True)
        self.assertFalse(content)
        self.assertIsNotNone(content)

    def test_index_if_no_path(self):
        """ Base wiki's url must have a trailing '/' so that the wiki's index
        file can contain relative links.
        """
        self.assertEqual(self.vcwiki.page_urlpath(''),
                         (u'wiki/%s/' % self.vcwiki.name))


class VCWikiBreadcrumbsTC(VCWikiTC):

    def wiki_breadcrumbs(self, wikipath):
        req = self.request()
        req.form = {'wikipath': wikipath}
        vcwiki = req.entity_from_eid(self.vcwiki.eid)
        return vcwiki.cw_adapt_to('IBreadCrumbs').breadcrumbs()

    def test_standard_breadcrumbs(self):
        """If we are not displaying a wiki page but the VCWiki instance itself,
        we should not use the custom breadcrumbs adapter"""
        self.assertEqual(self.vcwiki.cw_adapt_to('IBreadCrumbs').__class__,
                         IBreadCrumbsAdapter)

    def test_root(self):
        self.assertListEqual([(self.vcwiki.url, u'vcwiki')],
                             self.wiki_breadcrumbs(''))

    def test_simple(self):
        self.assertListEqual([(self.vcwiki.url, u'vcwiki'),
                              'hello'],
                             self.wiki_breadcrumbs('hello'))

    def test_subdir_file(self):
        self.assertListEqual([(self.vcwiki.url, u'vcwiki'),
                              (self.vcwiki.url + 'subject1', u'subject1'),
                              u'content1'],
                             self.wiki_breadcrumbs('subject1/content1'))

    def test_directory_has_no_index(self):
        self.assertListEqual([(self.vcwiki.url, u'vcwiki'),
                              'subject2',
                              'content2'],
                             self.wiki_breadcrumbs('subject2/content2'))

    def test_does_not_exist(self):
        self.assertListEqual([(self.vcwiki.url, u'vcwiki')],
                             self.wiki_breadcrumbs('does_not_exist'))


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
