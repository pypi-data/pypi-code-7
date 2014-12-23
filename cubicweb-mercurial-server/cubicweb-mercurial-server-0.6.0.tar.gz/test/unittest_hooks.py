# -*- coding: utf-8 -*-
import os.path as osp

import hglib

from cubicweb import Unauthorized, ValidationError, Binary
from cubicweb.devtools.testlib import CubicWebTC

from cubes.mercurial_server.testutils import MercurialServerTCMixin

class HooksBasicTC(MercurialServerTCMixin, CubicWebTC):
    # msc = MercurialServerConfig

    def test_nonascii_login(self):
        with self.admin_access.client_cnx() as cnx:
            user = self.create_user(cnx, u'françois')
            cnx.commit()
            with self.assertRaises(ValidationError):
                cnx.create_entity('SshPubKey',
                                  data=Binary('42'),
                                  reverse_public_key=user)
                cnx.commit()

    def _test_permission_prologue(self, cnx):
        access_key = cnx.user.public_key[0]
        repo = cnx.entity_from_eid(self.admin_user_repo)
        perm = repo.reverse_granted_on[0]
        self._assert_end_of_prologue(cnx, access_key.eid, perm)
        return cnx.entity_from_eid(access_key.eid), cnx.entity_from_eid(perm.eid)

    def _assert_end_of_prologue(self, cnx, access_key, perm):
        server_config = cnx.entity_from_eid(self.server_config)
        # Testing addition
        pubkey = self._hgadmin_file_content('keys', server_config.keys_subdir,
                                            cnx.user().login, str(access_key))
        self.assertEqual(pubkey, 'admin public key')

        # Check access.conf content
        content = self._hgadmin_file_content(server_config.conf_filename)
        self.assertEqual(content,
                         'write user=cw/%(login)s/%(key_eid)d repo=admin_repo\n'
                         % {'login': cnx.user().login,
                            'key_eid': access_key})

    def test_msc_regeneration_service(self):
        with self.admin_access.client_cnx() as cnx:
            access_key, perm = self._test_permission_prologue(cnx)
            access_key = access_key.eid
            perm = perm.eid
            userdesc = cnx.user.format_name_for_mercurial()
            msc = cnx.entity_from_eid(self.server_config)

            with msc.exec_in_hgadmin_clone("pouette", user=userdesc) as hgrepo:
                hgrepo.remove(osp.join(hgrepo.root(), 'keys', msc.keys_subdir))
                filename = osp.join(hgrepo.root(), msc.conf_filename_str)
                with open(filename, 'wb') as access:
                    access.write('')
            cnx.commit()

        with self.admin_access.client_cnx() as cnx:
            cnx.call_service('regenerate_hgadmin_repo', eid=self.server_config)
            self._assert_end_of_prologue(cnx, access_key, perm)

    def test_msc_deletion_ok(self):
        with self.admin_access.client_cnx() as cnx:
            server_config = cnx.entity_from_eid(self.server_config)
            conf_filename = server_config.conf_filename
            keys_dir = server_config.keys_subdir
            access_key, _perm = self._test_permission_prologue(cnx)

            cnx.execute('DELETE MercurialServerConfig X WHERE X eid %s' %
                        self.server_config)
            cnx.commit()

            # Check access.conf content
            content = self._hgadmin_file_content(conf_filename)
            self.assertEqual(content, '\n')

            with self.assertRaises(IOError):
                self._hgadmin_file_content('keys', keys_dir,
                                           cnx.user.login, str(access_key))

    def test_msc_deletion_with_rollback_inside(self):
        """ on deletion failure (i.e.: deletion order is issued
        but the trasnaction fails), the hgadmin repo files should
        be untouched -- though we may observe a pair of deletion commit/backout
        at the mercurial repository level
        """
        with self.admin_access.client_cnx() as cnx:
            access_key, perm = self._test_permission_prologue(cnx)
            access_key = access_key.eid
            perm = perm.eid
            cnx.execute('DELETE MercurialServerConfig X WHERE X eid %s' %
                        self.server_config)
            cnx.rollback()

        with self.admin_access.client_cnx() as cnx:
            self._assert_end_of_prologue(cnx, access_key, perm)

            # check that a 'backout' commit did happen
            server_config = cnx.entity_from_eid(self.server_config)
            hgrepo = hglib.open(server_config.hgadmin_repopath)
            alllogs = '\n'.join([entry[5] for entry in hgrepo.log()])
            self.assertIn('backout', alllogs)

    def test_permission_AUD(self):
        """ Test Adding, Updating and Deleting """
        with self.admin_access.client_cnx() as cnx:
            access_key, perm = self._test_permission_prologue(cnx)
            # Updating
            perm.cw_set(permission_level=u"write")
            cnx.commit() # Triggers hooks
            # Testing update
            # Check access.conf content
            server_config = cnx.entity_from_eid(self.server_config)
            content = self._hgadmin_file_content(server_config.conf_filename)
            self.assertEqual(content,
                             'write user=cw/%(login)s/%(key_eid)d repo=admin_repo\n'
                             % {'login': cnx.user.login,
                                'key_eid': access_key.eid,
                                })


            # Deleting the permission, thus the access_key relation
            perm.cw_delete()
            cnx.commit() # Triggers hooks
            #Check access.conf content
            content = self._hgadmin_file_content(server_config.conf_filename)
            self.assertEqual(content, '\n')


    def test_accesskey_AUD(self):
        """ Test Adding, Updating and Deleting"""
        with self.admin_access.client_cnx() as cnx:
            access_key, perm = self._test_permission_prologue(cnx)
            # Updating
            access_key.cw_set(data=Binary('24'))
            cnx.commit() # Triggers hooks
            # Testing update
            pubkey = self._hgadmin_file_content('keys', 'cw',
                                                cnx.user.login, str(access_key.eid))
            self.assertEqual(pubkey, '24')

            # Deleting the key, thus the access_key relation
            access_key.cw_delete()
            cnx.commit() # Triggers hooks
            # Testing deletion
            with self.assertRaises(IOError) as exc :
                pubkey = self._hgadmin_file_content('keys', 'cw',
                                                    cnx.user.login, str(access_key.eid))

            # Check access.conf content
            server_config = cnx.entity_from_eid(self.server_config)
            content = self._hgadmin_file_content(server_config.conf_filename)
            self.assertEqual(content, '\n')


    def test_consistent_permissions(self):
        """ Test at most one permissions for any (key, repo) pair"""
        with self.admin_access.client_cnx() as cnx:
            # Adding
            access_key = cnx.create_entity('SshPubKey',
                                           data=Binary('42'),
                                           reverse_public_key=cnx.user)
            perm = cnx.create_entity('MercurialServerPermission',
                                     permission_level=u'read',
                                     access_key=access_key,
                                     granted_on=self.admin_user_repo)
            cnx.commit() # Triggers hooks
            with self.assertRaises(ValidationError) as exc :
                # The relations access_key and repo are inlined ...
                perm = cnx.create_entity('MercurialServerPermission',
                                         permission_level=u'deny',
                                         access_key=access_key,
                                         granted_on=self.admin_user_repo)
                cnx.commit() # ... so are checked immediatly even without commit



class SchemaPermTC(MercurialServerTCMixin, CubicWebTC):

    def test_ordinary_user_AUD(self):
        with self.admin_access.client_cnx() as cnx:
            toto = self.create_user(cnx, u'toto').eid
            titi = self.create_user(cnx, u'titi').eid
            cnx.commit()

        with self.new_access('toto').client_cnx() as cnx:
            # toto cannot create a mercurial server config
            with self.assertRaises(Unauthorized):
                self.create_mercurial_server(cnx, 'for_toto')

        with self.new_access('toto').client_cnx() as cnx:
            # without a public key, toto cannot create a hosted repository
            toto_repo = self.create_mercurial_repo(cnx, 'toto_repo')
            with self.assertRaises(ValidationError) as wraperr:
                toto_repo.cw_set(hosted_by=self.server_config)
            self.assertEqual({'hosted_by': 'To create a hosted repository, toto must have a public key'},
                             wraperr.exception.args[1])

        with self.new_access('titi').client_cnx() as cnx:
            # user titi owns a Repository, but not hosted_by
            pubkey = cnx.create_entity('SshPubKey', data=Binary('titi public key'),
                                       reverse_public_key=titi)
            cnx.commit()
            titi_repo = self.create_mercurial_repo(cnx, 'titi_repo')
            cnx.commit()

        with self.new_access('toto').client_cnx() as cnx:
            pubkey = cnx.create_entity('SshPubKey',
                                       data=Binary('toto public key'),
                                       reverse_public_key=toto)
            self.create_mercurial_repo(cnx, 'toto_repo',
                                       hosted_by=self.server_config)
            cnx.commit()
        with self.admin_access.client_cnx() as cnx:
            toto_user = cnx.entity_from_eid(toto)
            toto_key = toto_user.public_key[0].eid
            toto_login = toto_user.login

            conf_filename = cnx.entity_from_eid(self.server_config).conf_filename
        content = self._hgadmin_file_content(conf_filename)
        self.assertListEqual(
            ['write user=cw/admin/%d repo=admin_repo' % self.admin_pubkey,
             'write user=cw/toto/%d repo=toto_repo' % toto_key],
            content.splitlines())
        with self.admin_access.client_cnx() as cnx:
            keys_subdir = cnx.entity_from_eid(self.server_config).keys_subdir
        pk = self._hgadmin_file_content('keys', keys_subdir,
                                        toto_login, str(toto_key))
        self.assertEqual('toto public key', pk)
        with self.admin_access.client_cnx() as cnx:
            cnx.execute('DELETE CWUser U WHERE U login "toto"')
            cnx.commit()
            conf_filename = cnx.entity_from_eid(self.server_config).conf_filename
        content = self._hgadmin_file_content(conf_filename)

        # all info about toto is gone
        self.assertEqual(['write user=cw/admin/%d repo=admin_repo' %
                          self.admin_pubkey],
                         content.splitlines())
        with self.admin_access.client_cnx() as cnx:
            keys_subdir = cnx.entity_from_eid(self.server_config).keys_subdir
        with self.assertRaises(IOError):
            self._hgadmin_file_content('keys', keys_subdir,
                                       toto_login, str(toto_key))

    def test_delete_hosted_by_non_owner(self):
        # just make sure non-owners of a Repository cannot change its
        # hosted_by relation (as per schema permissions)

        with self.admin_access.client_cnx() as cnx:
            toto = self.create_user(cnx, u'toto').eid
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            repo = cnx.entity_from_eid(self.admin_user_repo)
            self.assertNotIn(toto, set(o.eid for o in repo.owned_by))
            config = repo.hosted_by[0]
            with self.assertRaises(Unauthorized):
                cnx.execute('DELETE R hosted_by C WHERE R eid %d,'
                            '   C eid %d' %
                            (self.admin_user_repo, config.eid))
                cnx.commit()
        with self.admin_access.client_cnx() as cnx:
            repo = cnx.entity_from_eid(self.admin_user_repo)
            repopath = repo.source_url[7:]
            self.assertTrue(osp.exists(repopath))

    def test_repo_deletion_non_owner(self):
        # make sure non-owners cannot delete a repository (as per schema
        # permissions)
        with self.admin_access.client_cnx() as cnx:
            toto = self.create_user(cnx, u'toto')
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            repo = cnx.entity_from_eid(self.admin_user_repo)
            with self.assertRaises(Unauthorized):
                cnx.execute('DELETE Repository R WHERE R eid %d' %
                            self.admin_user_repo)
                cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            repo = cnx.entity_from_eid(self.admin_user_repo)
            repopath = repo.source_url[7:]
            self.assertTrue(osp.exists(repopath))


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
