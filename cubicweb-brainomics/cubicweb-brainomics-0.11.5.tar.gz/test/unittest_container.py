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
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.server.session import hooks_control

from cubes.medicalexp.config import SUBJECT_CONTAINER, ASSESSMENT_CONTAINER

from cubes.brainomics.importers.helpers import generate_container_relations
from cubes.brainomics.test.unittest_schema import create_subject_container_data


class BrainomicsContainersTC(CubicWebTC):
    """ Test proper behavior with respect to the Subject and Assessment containers. """

    def test_create_subject_container_instance(self):
        """ Container entities are created, according to the schema.
        """
        req = self.request()
        create_subject_container_data(req)

    def test_disjoint_container(self):
        e1, r1 = SUBJECT_CONTAINER.structure(self.vreg.schema)
        e2, r2 = ASSESSMENT_CONTAINER.structure(self.vreg.schema)
        self.assertEqual(e1.intersection(e2), set())
        self.assertEqual(r1.intersection(r2), set())

    def test_static_structure_subject(self):
        cfg = SUBJECT_CONTAINER
        self.assertEqual((frozenset(['related_diagnostics', 'related_therapies',
                                     'related_samples', 'related_biopsy',
                                     'taken_in_therapy', 'evaluation_for',
                                     'admission_of', 'step_of', 'survival_of',
                                     'report_on']),
                          frozenset(['Diagnostic', 'Therapy', 'DrugTake',
                                     'Biopsy', 'BiopsySample', 'BloodSample', 'CellCulture',
                                     'Admission', 'AdmissionStep',
                                     'SurvivalData', 'TherapyEvaluation',
                                     'AnatomicPathologyReport'])),
                         cfg.structure(self.vreg.schema))

    def test_static_structure_assessment(self):
        cfg = ASSESSMENT_CONTAINER
        self.assertEqual(
            (frozenset(['results_files', 'configuration_files', 'uses', 'generates',
                        'measure', 'file_entries', 'assessment', 'questionnaire_run',
                        'related_measure', 'measure', 'has_data', 'comments']),
             frozenset(['GenericMeasure', 'ExternalFile', 'FileSet', 'ScoreValue', 'File',
                        'QuestionnaireRun', 'Scan',
                        'GenomicMeasure', 'ColumnRef', 'Answer', 'IHCMeasure', 'IHCResult',
                        'CghResult', 'Mutation', 'PETData', 'MRIData', 'DMRIData', 'Comment'])),
            cfg.structure(self.vreg.schema))

    def test_generate_container_relations(self):
        session = self.session
        with hooks_control(session, session.HOOKS_ALLOW_ALL, 'container'):
            create_subject_container_data(session)
        rset = session.execute('Any X,Y WHERE X of_subject Y')
        self.assertEqual(len(rset), 0)
        rset = session.execute('Any X,Y WHERE X in_assessment Y')
        self.assertEqual(len(rset), 0)
        generate_container_relations(session)
        session = self.session
        rset = session.execute('Any X,Y WHERE X of_subject Y')
        self.assertEqual(len(rset), 4)
        rset = session.execute('Any X,Y WHERE X in_assessment Y')
        self.assertEqual(len(rset), 3)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
