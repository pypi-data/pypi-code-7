# -*- coding: utf-8 -*-
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

import zlib
import cPickle
from cubicweb.devtools.testlib import CubicWebTC


class RecordEntityTC(CubicWebTC):

    def test_add_entity_logged(self):
        with self.admin_access.repo_cnx() as cnx:
            auc_eid = cnx.create_entity('Auc', meal=u'chocolate',number=42).eid
            alain_eid = cnx.create_entity('Alain', drink=u'the', number=1024).eid
            mymy_eid = cnx.create_entity('Mymy', sport=u'dance', number=7).eid
            cnx.commit()

            rset = cnx.execute('TransactionLog X')
            self.assertEqual(1, len(rset))
            data = cPickle.loads(zlib.decompress(rset.get_entity(0, 0).data.getvalue()))
            expected = (('add_entity', (auc_eid, 'Auc', None)),
                        ('add_entity', (alain_eid, 'Alain', None)))
            self.assertSequenceEqual(expected, data)

    def test_delete_entity_logged(self):
        with self.admin_access.repo_cnx() as cnx:
            auc_eid = cnx.create_entity('Auc', meal=u'chocolate',number=42).eid
            alain_eid = cnx.create_entity('Alain', drink=u'the', number=1024).eid
            mymy_eid = cnx.create_entity('Mymy', sport=u'dance', number=7).eid
            cnx.commit()

            cnx.entity_from_eid(auc_eid).cw_delete()
            cnx.entity_from_eid(alain_eid).cw_delete()
            cnx.entity_from_eid(mymy_eid).cw_delete()
            cnx.commit()

            rset = cnx.execute('TransactionLog X')
            self.assertEqual(2, len(rset))
            data = cPickle.loads(zlib.decompress(rset.get_entity(1, 0).data.getvalue()))
            expected = (('delete_entity', (auc_eid, 'Auc', u'chocolate')),
                        ('delete_entity', (alain_eid, 'Alain', u'the')))
            self.assertEqual(set(expected), set(data))


    def test_update_entity_logged(self):
        with self.admin_access.repo_cnx() as cnx:
            auc_eid = cnx.create_entity('Auc', meal=u'chocolate',number=42).eid
            alain_eid = cnx.create_entity('Alain', drink=u'the', number=1024).eid
            mymy_eid = cnx.create_entity('Mymy', sport=u'dance', number=7).eid
            cnx.commit()

            cnx.entity_from_eid(auc_eid).cw_set(meal=u'ships', number=4)
            cnx.entity_from_eid(alain_eid).cw_set(drink=u'soja', number=2048)
            cnx.entity_from_eid(mymy_eid).cw_set(sport=u'running', number=21)
            cnx.commit()

            rset = cnx.execute('TransactionLog X')
            self.assertEqual(2, len(rset))
            data = cPickle.loads(zlib.decompress(rset.get_entity(1, 0).data.getvalue()))
            expected = (('update_entity', (auc_eid, 'Auc', ('meal', u'chocolate', u'ships'))),
                        ('update_entity', (auc_eid, 'Auc', ('number', 42, 4))),
                        ('update_entity', (alain_eid, 'Alain', ('drink', u'the', u'soja'))))
            self.assertEqual(set(expected), set(data))

    def test_add_relation_logged(self):
        with self.admin_access.repo_cnx() as cnx:
            auc_eid = cnx.create_entity('Auc', meal=u'chocolate',number=42).eid
            alain_eid = cnx.create_entity('Alain', drink=u'the', number=1024).eid
            mymy_eid = cnx.create_entity('Mymy', sport=u'dance', number=7).eid
            climbing_eid = cnx.create_entity('Climbing',
                                             location=u'Savoie',
                                             practiced_by=[auc_eid, alain_eid, mymy_eid]).eid
            diving_eid = cnx.create_entity('Diving',
                                           location=u'Martinique',
                                           practiced_by=[auc_eid, alain_eid, mymy_eid]).eid
            cnx.commit()

            rset = cnx.execute('TransactionLog X')
            self.assertEqual(1, len(rset))
            data = cPickle.loads(zlib.decompress(rset.get_entity(0, 0).data.getvalue()))
            expected = (('add_entity', (auc_eid, 'Auc', None)),
                        ('add_entity', (alain_eid, 'Alain', None)),
                        ('add_relation', ('practiced_by', (climbing_eid, auc_eid, ))),
                        ('add_relation', ('practiced_by', (diving_eid, mymy_eid))),
                        ('add_relation', ('practiced_by', (climbing_eid, alain_eid))),
                        ('add_relation', ('practiced_by', (diving_eid, alain_eid))))
            self.assertSequenceEqual(set(expected), set(data))

    def test_delete_relation_logged(self):
        with self.admin_access.repo_cnx() as cnx:
            auc_eid = cnx.create_entity('Auc', meal=u'chocolate',number=42).eid
            alain_eid = cnx.create_entity('Alain', drink=u'the', number=1024).eid
            mymy_eid = cnx.create_entity('Mymy', sport=u'dance', number=7).eid
            climbing_eid = cnx.create_entity('Climbing',
                                             location=u'Savoie',
                                             practiced_by=[auc_eid, alain_eid, mymy_eid]).eid
            diving_eid = cnx.create_entity('Diving',
                                           location=u'Martinique',
                                           practiced_by=[auc_eid, alain_eid, mymy_eid]).eid
            cnx.commit()

            cnx.execute('DELETE S practiced_by U WHERE U is IN (Auc, Alain), S is Climbing')
            cnx.execute('DELETE S practiced_by U WHERE U is IN (Mymy, Alain), S is Diving')
            cnx.commit()

            rset = cnx.execute('TransactionLog X')
            self.assertEqual(2, len(rset))
            data = cPickle.loads(zlib.decompress(rset.get_entity(1, 0).data.getvalue()))
            expected = (('delete_relation', ('practiced_by', (climbing_eid, auc_eid))),
                        ('delete_relation', ('practiced_by', (diving_eid, mymy_eid))),
                        ('delete_relation', ('practiced_by', (climbing_eid, alain_eid))),
                        ('delete_relation', ('practiced_by', (diving_eid, alain_eid))))
            self.assertEqual(set(expected), set(data))

    def test_emtpy_config(self):
        self.skipTest('CW does not provide an easy way to test this corner case.')



if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
