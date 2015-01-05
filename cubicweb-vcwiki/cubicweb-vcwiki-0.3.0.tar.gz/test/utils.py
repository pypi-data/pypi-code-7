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

"""cubicweb-vcwiki test utilities"""

from os import path as osp
from shutil import rmtree

from logilab.common.shellutils import unzip

# set up sys.path so we can find cubes.foo
import cubicweb.devtools

from cubes.vcsfile.testutils import VCSRepositoryTC, HGRCMixin

HERE = osp.dirname(__file__) or '.'

for repo in ('vcwiki',):
    repopath = osp.join(HERE, 'data', repo)
    if osp.exists(repopath):
        rmtree(repopath)
    unzip(osp.join(HERE, 'data', '%s.zip') % repo,  osp.join(HERE, 'data'))


class VCWikiTC(HGRCMixin, VCSRepositoryTC):
    _repo_path = u'vcwiki'

    def setup_database(self):
        """
        Create the vcwiki with write permission to managers from vcwiki.zip
        archive content.
        """
        self.vcwiki = self.execute(
            'INSERT VCWiki W: W name "vcwiki", W content_repo R, '
            'W content_file_extension "rst" '
            'WHERE R is Repository').get_entity(0, 0)
        # insert repository write permission for managers
        self.execute('INSERT CWPermission P: P name "write", P label "w p", '
                     'P require_group G, R require_permission P '
                     'WHERE R eid %(r)s, G name "managers"',
                     {'r': self.vcwiki.repository.eid})
        self.cleanup_repo()

    def cleanup_repo(self):
        """
        Restart from a fresh repository directory extracted from vcwiki.zip
        archive from the test/data directory.
        """
        if osp.exists(self.datapath('vcwiki')):
            rmtree(self.datapath('vcwiki'))
        unzip(self.datapath('vcwiki.zip'), self.datadir)

    def wiki_view(self, path, **form):
        """
        Helper that returns the view of the wiki page at path `path`, with
        other keyword args passed as web form dict items.
        """
        req = self.request()
        req.form = {'wikipath': path}
        req.form.update(form)
        vcwiki = req.entity_from_eid(self.vcwiki.eid)
        return self.view('vcwiki.view_page', vcwiki.as_rset(), req=req)

    def vcwiki_edit(self, path, content=u'new content', **kwargs):
        """ Helper that edit the wiki page at path `path` with content
        `content`, other keyword args being used as items of the web form.
        Returns a dict with web form and controller publication result.
        """
        req = self.request()
        req.form = {'vcwiki_eid': self.vcwiki.eid,
                    'wikipath': path,
                    'content': content,
                    'message': u'my commit',
                    'rev': 'tip'}
        req.form.update(kwargs)
        return {'form': req.form,
                'result': self.ctrl_publish(req, ctrl='vcwiki.edit_page')}
