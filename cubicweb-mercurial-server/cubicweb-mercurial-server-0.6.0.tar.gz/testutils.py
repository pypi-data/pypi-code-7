# -*- coding: utf-8 -*-
# copyright 2011 Florent Cayré (FRANCE), all rights reserved.
# contact florent.cayre@gmail.com
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

import tempfile
import os, os.path as osp
import shutil
from contextlib import contextmanager

import hglib

from cubicweb import Binary

from cubes.vcsfile import bridge, testutils


class MercurialServerTCMixin(testutils.HGRCMixin):
    debug = False

    @classmethod
    def fs_repopath(cls, reponame):
        return osp.join(cls.datadir, 'repos', reponame)

    @classmethod
    def fs_create_mercurial_repopath(cls, reponame):
        """Create repository path, possibly deleting existing content"""
        repopath = cls.fs_repopath(reponame)
        if osp.isdir(repopath):
            shutil.rmtree(repopath)
        os.makedirs(repopath)
        return repopath

    @classmethod
    def create_mercurial_repo(cls, cnx, reponame, **kwargs):
        """ Create a mercurial repository """
        repopath = cls.fs_create_mercurial_repopath(reponame)
        return cnx.create_entity('Repository',
                                 title=unicode(reponame),
                                 type=u'mercurial',
                                 source_url=u'file://' + repopath,
                                 **kwargs)

    @classmethod
    def fs_create_mercurial_server(cls):
        # mercurial server creates repo directory recursively but this is not
        # the case in this fake env: we need to create receiving directory first
        repopath = cls.fs_create_mercurial_repopath('hgadmin')
        source_url = 'file://' + repopath
        hglib.init(source_url.encode('ascii'))
        return repopath

    @classmethod
    def create_mercurial_server(cls, cnx, name='hgadmin'):
        name = unicode(name)
        return cnx.create_entity('MercurialServerConfig',
                                 name=name,
                                 base_url=u'file://' + cls.datapath('repos'),
                                 hgadmin_path=name)

    def refresh(self):
        with self.repo.internal_cnx() as cnx:
            bridge.import_content(cnx, commitevery=1, raise_on_error=True)

    def setup_database(self):
        '''initialize a fake hgadmin repository'''
        super(MercurialServerTCMixin, self).setup_database()
        with self.admin_access.client_cnx() as cnx:
            self.fs_create_mercurial_server()
            self.server_config = self.create_mercurial_server(cnx).eid
            cnx.commit()
        self.refresh()
        with self.admin_access.client_cnx() as cnx:
            self.admin_pubkey = cnx.create_entity(
                    'SshPubKey', name=u'admin-pubkey',
                    data=Binary('admin public key'),
                    reverse_public_key=cnx.user).eid
            cnx.commit()
            self.admin_user_repo = self.create_mercurial_repo(
                cnx, 'admin_repo', hosted_by=self.server_config).eid
            cnx.commit()
        self.refresh()

    def tearDown(self):
        '''removes the fake hgadmin repository'''
        super(MercurialServerTCMixin, self).tearDown()
        # wipe local repo caches: they get old wrong default push paths
        shutil.rmtree(osp.join(self.config.appdatahome, 'repo_cache'))
        if osp.isdir(self.datapath('repos')):
            if not self.debug:
                shutil.rmtree(self.datapath('repos'), ignore_errors=True)
            else:
                print ("[DEBUG] repositories can be found in %s" %
                       self.datapath('repos'))

    def _hgadmin_file_content(self, *path):
        path = tuple(str(x) for x in path)
        repo = hglib.open(self.fs_repopath('hgadmin'))
        repo.update()
        fullpath = osp.join(repo.root(), *path)
        with open(fullpath, 'r') as f:
            return f.read()
