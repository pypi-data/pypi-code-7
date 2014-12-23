import os.path as osp

import hglib

from cubicweb import Binary, ValidationError
from cubicweb.devtools.testlib import CubicWebTC

from cubes.mercurial_server.testutils import MercurialServerTCMixin


class EntitiesBasicTC(MercurialServerTCMixin, CubicWebTC):
    """ Test features of entities which does not require any mercurial server.
    """

    def test_exec_in_hgadmin_clone(self):
        with self.admin_access.client_cnx() as cnx:
            server_config = cnx.entity_from_eid(self.server_config)
            with server_config.exec_in_hgadmin_clone('test commit msg') as repo:
                filename = osp.join(repo.root(), 'whatever.txt')
                with open(filename, 'a') as fobj:
                    fobj.write('Hello World\n')
                repo.add(filename)

        content = self._hgadmin_file_content('whatever.txt')
        self.assertEqual(content, 'Hello World\n')


    def test_mercurial_server_permission(self):
        with self.admin_access.client_cnx() as cnx:
            access_key = cnx.create_entity('SshPubKey',
                                           data=Binary('42'),
                                           reverse_public_key=cnx.user)

            perm = cnx.create_entity('MercurialServerPermission',
                                     permission_level=u'read',
                                     access_key=access_key,
                                     granted_on=self.admin_user_repo)

            self.assertEqual(perm.server_config.eid, self.server_config)
            self.assertEqual(perm.pubkey.getvalue(), '42')

    def test_mercurial_server_access_key(self):
        with self.admin_access.client_cnx() as cnx:
            access_key = cnx.create_entity('SshPubKey',
                                           data=Binary('42'),
                                           reverse_public_key=cnx.user)

            perm = cnx.create_entity('MercurialServerPermission',
                                     permission_level=u'read',
                                     access_key=access_key,
                                     granted_on=self.admin_user_repo)
            mcs = access_key.mercurial_server_configs
            self.assertListEqual([m.eid for m in mcs], [self.server_config])

    def test_access_conf_generation(self):
        with self.admin_access.client_cnx() as cnx:
            msc = cnx.entity_from_eid(self.server_config)
            access_key = cnx.user.public_key[0]
            self.assertEqual(msc.generate_access_conf(),
                             'write user=cw/%(login)s/%(key_eid)d repo=admin_repo\n'
                             % {'login': cnx.user.login,
                                'key_eid': access_key.eid,
                               })


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
