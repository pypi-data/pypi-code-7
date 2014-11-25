# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

""" Schema test """

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.web.views import uicfg

from cubes.brainomics.views.primary import BrainomicsPrimaryView


class BrainomicsUICFGTC(CubicWebTC):
    """ Test proper uicfg behavior, see https://www.cubicweb.org/ticket/3489097 """

    def setup_database(self):
        """ Several entities involving composite relations are created,
            according to the schema.
        """
        # Clean uicfg for test
        uicfg.primaryview_display_ctrl._relrsetdefs = {}
        uicfg.primaryview_display_ctrl._attrrsetdefs = {}
        # Add entities
        req = self.request()
        t_study = req.create_entity('Study', name=u'Test study',
                                    data_filepath=u'test/data/filepath')
        t_card = req.create_entity('Card', title=u'This is a card.',
                                   reverse_wiki=t_study)
        t_subj = req.create_entity('Subject', identifier=u'test_subj',
                                   gender=u'unknown', handedness=u'mixed')
        t_center = req.create_entity('Center', identifier=u'center_id',
                                     name=u'Test center name')
        t_assessment = req.create_entity('Assessment',
                                         related_study=t_study,
                                         reverse_holds=t_center,
                                         reverse_concerned_by=t_subj)

    def get_display_rset(self, req, entity, type='relations'):
        pview = BrainomicsPrimaryView(req)
        uicfg_reg = req.vreg['uicfg']
        pview.display_ctrl = uicfg_reg.select('primaryview_display_ctrl',
                                              req, entity=entity)
        return list(pview.iterate_display_rset(entity, type))

    def add_center_uicfg(self):
        _pvdc = uicfg.primaryview_display_ctrl
        _pvdc.display_rset('Center', 'relations',
                           {'rql': 'Any S WHERE S concerned_by Y, X holds Y',
                            'vid': 'table',
                            'order': 1,
                            'label': _('Subjects')})

    def test_uihelper_setdefs(self):
        # Add uicfg display_rset
        _pvdc = uicfg.primaryview_display_ctrl
        self.add_center_uicfg()
        _pvdc.display_rset('Gene', 'relations',
                           {'rql': 'Any CGH WHERE CGH genomic_region GR, GR genes X',
                            'vid': 'region-genmeas-table-view',
                            'order': 1,
                            'label': _('CGH results')})
        self.assertEqual(uicfg.primaryview_display_ctrl._attrrsetdefs, {})
        self.assertEqual(uicfg.primaryview_display_ctrl._relrsetdefs['Center'],
                         [{'rql': 'Any S WHERE S concerned_by Y, X holds Y',
                           'order': 1, 'vid': 'table', 'label': u'Subjects'}])
        self.assertEqual(uicfg.primaryview_display_ctrl._relrsetdefs['Gene'],
                         [{'rql': 'Any CGH WHERE CGH genomic_region GR, GR genes X',
                           'vid': 'region-genmeas-table-view',
                           'order': 1,
                           'label': _('CGH results')}])

    def test_uihelper_iterate_rset_relations(self):
        # Add uicfg display_rset
        self.add_center_uicfg()
        req = self.request()
        entity = req.find_one_entity('Center', identifier=u'center_id')
        display_rset = self.get_display_rset(req, entity)
        self.assertEqual(len(display_rset), 1)
        self.assertEqual(display_rset[0][0], 1)
        self.assertEqual(display_rset[0][1], u'Subjects')
        self.assertTrue(display_rset[0][2].startswith('<div id'))

    def test_uihelper_iterate_rset_attributes(self):
        # Add uicfg display_rset
        _pvdc = uicfg.primaryview_display_ctrl
        _pvdc.display_rset('Center', 'attributes',
                           {'callback': lambda x:x.identifier,
                            'order': 2,
                            'label': _('Test callback')})
        self.add_center_uicfg()
        req = self.request()
        entity = req.find_one_entity('Center', identifier=u'center_id')
        display_rset = self.get_display_rset(req, entity, 'attributes')
        self.assertEqual(len(display_rset), 1)
        self.assertEqual(display_rset, [(2, u'Test callback', u'center_id')])

    def test_uihelper_iterate_rset_callback(self):
        self.add_center_uicfg()
        req = self.request()
        _pvdc = uicfg.primaryview_display_ctrl
        _pvdc.display_rset('Center', 'relations',
                           {'callback': lambda x:x.identifier,
                            'order': 2,
                            'label': _('Test callback')})
        entity = req.find_one_entity('Center', identifier=u'center_id')
        display_rset = self.get_display_rset(req, entity)
        self.assertEqual(len(display_rset), 2)
        self.assertEqual(display_rset[1], (2, u'Test callback', u'center_id'))

    def test_uihelper_order(self):
        req = self.request()
        _pvdc = uicfg.primaryview_display_ctrl
        _pvdc.display_rset('Center', 'relations',
                           {'rql': 'Any S WHERE S concerned_by Y, X holds Y',
                            'vid': 'table',
                            'order': 2,
                            'label': _('Subjects 2')})
        _pvdc.display_rset('Center', 'relations',
                           {'rql': 'Any S WHERE S concerned_by Y, X holds Y',
                            'vid': 'table',
                            'order': 0,
                            'label': _('Subjects 0')})
        _pvdc.display_rset('Center', 'relations',
                           {'callback': lambda x:x.identifier,
                            'order': 1,
                            'label': _('Subjects 1')})
        entity = req.find_one_entity('Center', identifier=u'center_id')
        pview = BrainomicsPrimaryView(req)
        html = []
        html_rel = []
        pview.w = html.append
        pview.render_relation = lambda x,y: html_rel.append((x,y))
        pview.render_entity(entity)
        self.assertEqual(html_rel[0][0], 'Subjects 0')
        self.assertEqual(html_rel[1][0], 'Subjects 1')
        self.assertEqual(html_rel[2][0], 'Subjects 2')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
