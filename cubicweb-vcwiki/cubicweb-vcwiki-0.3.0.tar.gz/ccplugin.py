# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-vcwiki command plugins"""

import hglib

from logilab.common.shellutils import ASK

from cubicweb import cwconfig
from cubicweb.server.utils import manager_userpasswd
from cubicweb.dbapi import in_memory_repo_cnx
from cubicweb.toolsutils import Command, CONNECT_OPTIONS
from cubicweb.cwctl import CWCTL


class CreateVCWiki(Command):
    """Create and setup a VCWiki with associated repository.

    Write permissions for 'users' and 'managers' are granted on the newly
    created Repository.
    If the Mercurial repository is not initial (or does not exists), the
    command will do it.
    """
    name = 'new-vcwiki'
    arguments = '<instance> <wikiname> <repopath>'
    min_args = 3
    max_args = 3
    options = CONNECT_OPTIONS

    def run(self, args):
        appid = args.pop(0)
        config = cwconfig.instance_configuration(appid)
        user, password = self.config.user, self.config.password
        if not password:
            user, password = manager_userpasswd(user=user, msg='')
        _, cnx = in_memory_repo_cnx(config, login=user, password=password)
        self.cnx = cnx
        wikiname, repopath = args
        try:
            self.add_vcwiki(wikiname, repopath)
        except:
            self.cnx.rollback()
            raise
        else:
            self.cnx.commit()
            self.setup_hgrepo(repopath)
        finally:
            self.cnx.close()

    def add_vcwiki(self, wikiname, repopath):
        """Add a VCWiki and corresponding Repository, with write permission
        for 'users' and 'managers'"""
        req = self.cnx.request()
        repos = req.create_entity(
            'Repository', title=u'Repository for %s' % wikiname,
            path=unicode(repopath), type=u'mercurial')
        wiki = req.create_entity(
            'VCWiki', name=unicode(wikiname), content_file_extension=u'rst',
            content_repo=repos)
        perm = req.create_entity(
            'CWPermission', name=u'write',
            label=u'write permission for %s repository' % wikiname)
        for group in (u'users', u'managers'):
            group = req.find_one_entity('CWGroup', name=group)
            perm.cw_set(require_group=group)
        repos.cw_set(require_permission=perm)

    def setup_hgrepo(self, repopath):
        """Check that the Mercurial repository is operational."""
        try:
            hglib.open(repopath).close() # Test existence, then close it.
        except hglib.error.ServerError:
            if ASK.confirm('The Mercurial repository for the Wiki does not seem to '
                           'exist, create it?'):
                hglib.init(repopath)
                print 'Repository %s initialized' % repopath


CWCTL.register(CreateVCWiki)
