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

def create_subject_container_data(req):
    """ Several entities involving composite relations are created,
        according to the schema.
    """
    t_study = req.create_entity('Study', name=u'Test study',
                                data_filepath=u'test/data/filepath')
    t_card = req.create_entity('Card', title=u'This is a card.',
                               reverse_wiki=t_study)
    t_subj = req.create_entity('Subject', identifier=u'test_subj',
                               gender=u'unknown', handedness=u'mixed')
    t_adm = req.create_entity('Admission', admission_of=t_subj,
                              admission_in=t_study)
    t_step = req.create_entity('AdmissionStep', step_of=t_adm, name=u'step')
    t_ther = req.create_entity('Therapy', reverse_related_therapies=t_subj)
    t_body = req.create_entity('BodyLocation', identifier=u'bd', name=u'bd')
    t_disease = req.create_entity('Disease', identifier=u'di', name=u'di')
    t_diag = req.create_entity('Diagnostic', reverse_related_diagnostics=t_subj,
                               diagnostic_location=t_body,
                               diagnosed_disease=t_disease)
    t_center = req.create_entity('Center', identifier=u'Test center ID',
                                 name=u'Test center name')
    t_assessment = req.create_entity('Assessment',
                                     related_study=t_study,
                                     reverse_holds=t_center,
                                     reverse_concerned_by=t_subj)
    t_questionnaire = req.create_entity('Questionnaire', name=u'Test quiz',
                                        identifier=u'test_quiz_id',
                                        type=u'test')
    t_qrun = req.create_entity('QuestionnaireRun',
                               user_ident=u'test_qrun_uident',
                               instance_of=t_questionnaire,
                               reverse_generates=t_assessment,
                               concerns=t_subj,
                               related_study=t_study)
    t_comm = req.create_entity('Comment', content=u'This is a test comment',
                               comments=t_qrun)
    t_score_def = req.create_entity('ScoreDefinition', name=u'Test score def',
                                    type=u'string')
    t_score_val = req.create_entity('ScoreValue', definition=t_score_def,
                                    text=u'test score val', measure=t_qrun)

class BrainomicsSchemaTC(CubicWebTC):
    """ Test proper behavior with respect to the composite relations. """

    def setup_database(self):
        """ Several entities involving composite relations are created,
            according to the schema.
        """
        req = self.request()
        create_subject_container_data(req)

    def test_cleanup_on_qrun_delete(self):
        """ Test that on QuestionnaireRun deletion, the Comment,
            ExternalResource and ScoreValue are deleted, but the Subject,
            Assessment and Study are not deleted.
        """
        req = self.request()
        qrun_eid = req.execute('Any X WHERE X is QuestionnaireRun').get_entity(0, 0).eid
        req.execute('Delete QuestionnaireRun X WHERE X eid %(qreid)s', {'qreid': qrun_eid})
        self.commit()
        db_comm = req.execute('Any X WHERE X is Comment')
        if db_comm:
            self.fail('The Comment was not deleted')
        db_ext_res = req.execute('Any X WHERE X is ExternalFile')
        if db_ext_res:
            self.fail('The ExternalResource was not deleted')
        db_score_val = req.execute('Any X WHERE X is ScoreValue')
        if db_score_val:
            self.fail('The ScoreValue was not deleted')
        db_subj = req.execute('Any X WHERE X is Subject')
        if not db_subj:
            self.fail('The Subject was deleted')
        db_assess = req.execute('Any X WHERE X is Assessment')
        if not db_assess:
            self.fail('The Assessment was deleted')
        db_study = req.execute('Any X WHERE X is Study')
        if not db_study:
            self.fail('The Study was deleted')

    def test_cleanup_on_study_delete(self):
        """ Test that on Study deletion, the QuestionnaireRun and Card are deleted.
        """
        req = self.request()
        study_eid = req.execute('Any X WHERE X is Study').get_entity(0, 0).eid
        db_card = req.execute('Any X WHERE X is Card, X title "This is a card."')
        if not db_card:
            self.fail('The test Card was not founs')
        # Delete Assessment first:
        req.execute('DELETE Assessment X WHERE X related_study Y, Y eid %(studeid)s',
                    {'studeid': study_eid})
        # Also delete Admission, for cardinality constraints reasons:
        req.execute('DELETE Admission X WHERE X admission_in Y, Y eid %(studeid)s',
                    {'studeid': study_eid})
        req.execute('DELETE Study X WHERE X eid %(studeid)s', {'studeid': study_eid})
        self.commit()
        db_qrun = req.execute('Any X WHERE X is QuestionnaireRun')
        if db_qrun:
            self.fail('The QuestionnaireRun was not deleted')
        db_card = req.execute('Any X WHERE X is Card, X title "This is a card."')
        if db_card:
            self.fail('The Card was not deleted')

    def test_cleanup_on_assessment_delete(self):
        """ Test that on Assessment deletion, the QuestionnaireRun is deleted, but
            the Study is not deleted.
        """
        req = self.request()
        assess_eid = req.execute('Any X WHERE X is Assessment').get_entity(0, 0).eid
        db_qrun = req.execute('Any X WHERE X is QuestionnaireRun')
        if not db_qrun:
            self.fail('No QuestionnaireRun was found')
        req.execute('DELETE Assessment X WHERE X eid %(aseid)s', {'aseid': assess_eid})
        self.commit()
        db_qrun = req.execute('Any X WHERE X is QuestionnaireRun')
        if db_qrun:
            self.fail('The QuestionnaireRun was not deleted')
        db_study = req.execute('Any X WHERE X is Study')
        if not db_study:
            self.fail('The Study was deleted')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
