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


class BrainomicsEntitiesTC(CubicWebTC):

    def _create_subject(self):
        req = self.request()
        study = req.create_entity('Study', name=u'Test study')
        subj = req.create_entity('Subject', identifier=u'test_subj')
        sdef = req.create_entity('ScoreDefinition', name=u'Test score def', type=u'string')
        sval = req.create_entity('ScoreValue', definition=sdef, text=u'test score val')
        return study, subj, sdef, sval

    def _create_measure(self, study, subj):
        req = self.request()
        center = req.create_entity('Center', identifier=u'Test center ID',
                                   name=u'Test center name')
        assessment = req.create_entity('Assessment',
                                       related_study=study,
                                       reverse_holds=center,
                                       reverse_concerned_by=subj)
        questionnaire = req.create_entity('Questionnaire', name=u'Test quiz',
                                          identifier=u'test_quiz_id',
                                          type=u'test')
        qrun = req.create_entity('QuestionnaireRun',
                                 user_ident=u'test_qrun_uident',
                                 instance_of=questionnaire,
                                 reverse_generates=assessment,
                                 concerns=subj,
                                 related_study=study)
        return qrun

    def _create_sample(self, study, subj):
        req = self.request()
        biopsy = req.create_entity('Biopsy',
                                   related_study=study,
                                   reverse_related_samples=subj)
        return biopsy

    def test_score_value_subject_1(self):
        study, subj, sdef, sval = self._create_subject()
        subj.cw_set(related_infos=sval)
        self.commit()
        self.assertEqual(sval.subject, subj)

    def test_score_value_subject_2(self):
        study, subj, sdef, sval = self._create_subject()
        qrun = self._create_measure(study, subj)
        sval.cw_set(measure=qrun)
        self.commit()
        self.assertEqual(sval.subject, subj)

    def test_score_value_subject_3(self):
        study, subj, sdef, sval = self._create_subject()
        biopsy = self._create_sample(study, subj)
        sval.cw_set(score_of_sample=biopsy)
        self.commit()
        self.assertEqual(sval.subject, subj)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
