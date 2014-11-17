from cubicweb import Unauthorized
from cubicweb.devtools.testlib import CubicWebTC

class SecurityTC(CubicWebTC):

    def test_same_user_token_read(self):
        req = self.request()
        self.create_user(req, 'toto')
        with self.login('toto') as cu:
            req = self.request()
            token = req.create_entity('AuthToken', id=u'122', token=u'456')
            self.commit()
            self.assertEqual(cu.execute('Any T WHERE AT token T, AT token_for_user U, U login %(login)s',
                                        {'login': 'toto'}).rowcount, 1)

    def test_other_user_no_token_read(self):
        req = self.request()
        self.create_user(req, 'toto')
        self.create_user(req, 'babar')
        with self.login('toto') as cu:
            req = self.request()
            req.create_entity('AuthToken', id=u'122', token=u'456')
        self.commit()
        with self.login('babar') as cu:
            rset = cu.execute('Any T WHERE AT token T, AT token_for_user U, U login %(login)s',
                              {'login': 'toto'})
            self.assertFalse(rset)

    def test_user_token_add(self):
        req = self.request()
        self.create_user(req, 'toto')
        with self.login('toto') as cu:
            req = self.request()
            token = req.create_entity('AuthToken', id=u'122')
            self.commit()
        token = self.session.entity_from_eid(token.eid)
        self.assertEqual(128, len(token.token))

    def test_user_token_modify(self):
        req = self.request()
        self.create_user(req, 'toto')
        with self.login('toto') as cu:
            req = self.request()
            token = req.create_entity('AuthToken', id=u'122')
            self.commit()
            cu.execute('SET AT enabled True WHERE AT eid %(e)s', {'e':token.eid})
            self.commit()
            with self.assertRaises(Unauthorized):
                cu.execute('SET AT token "babar" WHERE AT eid %(e)s', {'e':token.eid})
                self.commit()
            self.rollback()

    def test_user_token_delete(self):
        req = self.request()
        self.create_user(req, 'toto')
        with self.login('toto') as cu:
            req = self.request()
            token = req.create_entity('AuthToken')
            self.commit()
            cu.execute('DELETE AuthToken T WHERE T eid %(e)s', dict(e=token.eid))
        self.commit()

    def test_manager_do_enabled_modify(self):
        req = self.request()
        self.create_user(req, 'toto')
        with self.login('toto') as cu:
            req = self.request()
            token = req.create_entity('AuthToken', id=u'122', token=u'456')
            self.commit()
        token = self.session.entity_from_eid(token.eid)
        with self.assertRaises(Unauthorized):
            token.cw_set(enabled=True)
            self.commit()

    def test_manager_no_token_modify(self):
        req = self.request()
        token = req.create_entity('AuthToken', id=u'122', token=u'456')
        self.commit()
        with self.assertRaises(Unauthorized):
            token.cw_set(token=u'babar')
            self.commit()


if __name__ == "__main__":
    from logilab.common.testlib import unittest_main
    unittest_main()
