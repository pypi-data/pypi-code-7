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

"""cubicweb-vcwiki restructured text rendering tests"""


from utils import VCWikiTC


class VCWikiViewTC(VCWikiTC):

    def assertEntitled(self, expected_title, html):
        self.assertEqual([u'vcwiki - %s' % expected_title],
                         html.find_tag('title'))

    def test_existing_wiki_page(self):
        html = self.wiki_view('subject2/content2')
        self.assertEntitled('content2', html)
        self.assertTrue('content of subject2/content2.rst' in html)

    def test_existing_wiki_page_with_revision(self):
        req = self.request()
        # Check test prerequisite
        vc0 = self.vcwiki.content('hello.rst', revision=0)
        vc1 = self.vcwiki.content('hello.rst') # last revision
        new_words = 'modified since its creation'
        self.assertNotIn(new_words, vc0.decode('ascii'))
        self.assertIn(new_words, vc1.decode('ascii'))
        # Check new added content is not present in the view of the old revision
        html = self.wiki_view('hello', rev='0')
        self.assertNotIn(new_words, html)

    def test_non_existing_wiki_page(self, link=True):
        html = self.wiki_view('does_not_exist')
        self.assertEntitled('New wiki page', html)
        self.assertIn('This wiki page does not exist.', html)
        check = getattr(self, 'assert' + str(link))
        check(html.has_link('Create this wiki page?'))

    def test_non_existing_wiki_page_user_cannot_edit(self):
        self.create_user(self.request(), u'spammer')
        with self.login(u'spammer'):
            self.test_non_existing_wiki_page(link=False)


class WikiReSTDirectiveTC(VCWikiTC):

    base_url = u'http://testing.fr/cubicweb/wiki/vcwiki'

    def assertHasLink(self, text, html, url_path, klass):
        attrs = {'class': klass, 'href': self.base_url + url_path}
        links = tuple(html.matching_nodes('a', **attrs))
        self.assertEqual(1, len(links))
        self.assertEqual(text, links[0].text)

    def test_links(self):
        html = self.wiki_view('subject1/with_links')
        self.assertHasLink('simple relative link to content1',
                           html,
                           u'/subject1/content1', u'reference')
        self.assertHasLink('relative link to content2',
                           html,
                           u'/subject2/content2', u'reference')
        self.assertHasLink('absolute link to with_links.rst',
                           html,
                           u'/subject1/with_links', u'reference')
        self.assertHasLink('link to non-existing page',
                           html,
                           u'/subject1/does_not_exist',
                           u'doesnotexist reference')





if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
