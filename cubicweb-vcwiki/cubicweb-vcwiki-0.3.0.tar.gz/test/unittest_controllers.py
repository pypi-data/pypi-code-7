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

"""cubicweb-vcwiki controllers' tests"""

from os import path as osp

import hglib
from cubicweb.web import Redirect

from utils import VCWikiTC


class VCWikiViewControllerTC(VCWikiTC):

    def publish_wiki_path(self, path, wikiid='vcwiki'):
        req = self.request()
        req.form = {'wikiid': wikiid, 'wikipath': path}
        return self.ctrl_publish(req, ctrl='wiki')

    def test_wiki_does_not_exist(self):
        self.assertTrue('no access to this view'
                        in self.publish_wiki_path('', wikiid='does_not_exist'))

    def test_wiki_page(self):
        self.assertTrue('content of subject2/content2'
                        in self.publish_wiki_path('subject2/content2'))

    def test_image(self):
        repo_path = self.vcwiki.repository.localcachepath
        fname = '120px-Crystal_Clear_app_kedit.png'
        image = self.publish_wiki_path(fname)
        with hglib.open(repo_path) as repo:
            image_file = repo.cat([osp.join(repo_path, fname)], rev='tip')
        self.assertEqual(image, image_file,
                         'wrong image content delivery')


class VCWikiEditControllerTC(VCWikiTC):

    def setup_database(self):
        super(VCWikiEditControllerTC, self).setup_database()
        req = self.request()
        rql = 'Any X WHERE X is CWGroup, X name "managers"'
        managers = req.execute(rql).get_entity(0, 0)
        req.create_entity('CWPermission',
                          name=u'write',
                          label=u'vcwiki write',
                          require_group=managers,
                          reverse_require_permission=self.vcwiki.repository)
        self.commit()

    def check_edition_result(self, form, check_content_value=None, result=None):
        fpath = form['wikipath'] + '.%s' % self.vcwiki.content_file_extension
        vcontent = self.vcwiki.content(fpath)
        self.assertIsNotNone(vcontent,
                             'could not find "%s" in current wiki' % fpath)
        if check_content_value is None:
            check_content_value = form['content']
        self.assertEqual(check_content_value, vcontent)

    def test_creation(self):
        self.check_edition_result(**self.vcwiki_edit(u'newsubject/dummy'))

    def test_edition(self):
        self.check_edition_result(**self.vcwiki_edit(u'subject2/content2'))

    def test_deletion(self):
        self.vcwiki_edit(u'subject2/content2', content=u'')
        vcontent = self.vcwiki.content(u'subject2/content2.rst',
                                       allow_deleted=True)
        self.assertFalse(vcontent)
        self.assertIsNotNone(vcontent)

    def test_preview_creation(self):
        result = self.vcwiki_edit(u'newsubject/preview',
                                  __action_preview = 'button_preview')['result']
        self.assertIn('new content', result)

    def test_preview_edition(self):
        initial_content = self.vcwiki.content(
            u'subject2/content2.rst')
        self.check_edition_result(
            check_content_value=initial_content,
            **self.vcwiki_edit(u'subject2/content2',
                               __action_preview = 'button_preview'))


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
