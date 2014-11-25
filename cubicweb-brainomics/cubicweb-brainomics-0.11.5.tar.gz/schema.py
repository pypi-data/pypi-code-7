# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2013 CEA (Saclay, FRANCE), all rights reserved.
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

"""cubicweb-brainomics schema"""
from itertools import chain

from cubicweb.schemas.base import CWUser
from yams.buildobjs import RelationDefinition, SubjectRelation, String

from cubes.questionnaire.schema import QuestionnaireRun, Questionnaire, Question
from cubes.neuroimaging.schema import Scan, AnatomicalRegion
from cubes.genomics.schema import GenomicMeasure, ColumnRef, Gene
from cubes.medicalexp.schema  import (Assessment, ProcessingRun, ScoreDefinition, ScoreValue,
                                      Diagnostic, TechnicalAnalysis, Subject)
from cubes.clinipath.schema import Biopsy, BiopsySample, CellCulture, BloodSample, IHCMeasure


# Diagnostic/TechnicalAnalysis
for etype in ('QuestionnaireRun', 'Scan', 'GenomicMeasure'):
    Diagnostic.add_relation(SubjectRelation(etype, cardinality='**'), name='based_on')
    # No composite for TechnicalAnalysis (for container)
    TechnicalAnalysis.add_relation(SubjectRelation(etype, cardinality='**'), name='performed_on')
for etype in ('Biopsy', 'BiopsySample', 'CellCulture', 'BloodSample'):
    Diagnostic.add_relation(SubjectRelation(etype, cardinality='**'), name='based_on')
    # No composite for TechnicalAnalysis (for container)
    TechnicalAnalysis.add_relation(SubjectRelation(etype, cardinality='**'), name='analysis_of_sample')
for etype in ('QuestionnaireRun', 'Scan', 'GenomicMeasure', 'IHCMeasure'):
    ProcessingRun.add_relation(SubjectRelation(etype, cardinality='**'), name='inputs')
    ProcessingRun.add_relation(SubjectRelation(etype, cardinality='**'), name='outputs')
    Assessment.add_relation(SubjectRelation(etype, cardinality='**',
                                            composite='subject'), name='uses')
    Assessment.add_relation(SubjectRelation(etype, cardinality='**',
                                            composite='subject'), name='generates')
# Score -> Measure
for etype in ('QuestionnaireRun', 'Scan', 'GenomicMeasure', 'IHCMeasure'):
    ScoreValue.add_relation(SubjectRelation(etype, cardinality='?*', inlined=True,
                                            composite='object'), name='measure')
for etype in ('Biopsy', 'BiopsySample', 'CellCulture', 'BloodSample'):
    ScoreValue.add_relation(SubjectRelation(etype, cardinality='?*', inlined=True), name='score_of_sample')
# Measure -> Subject
for etype_class in (QuestionnaireRun, Scan, GenomicMeasure, IHCMeasure):
    etype_class.add_relation(SubjectRelation(('Subject', 'SubjectGroup'),
                                             cardinality='1*', inlined=True), name='concerns')
    etype_class.add_relation(SubjectRelation('Study', cardinality='1*', inlined=True,
                                             composite='object'), name='related_study')
    etype_class.add_relation(SubjectRelation('Study', cardinality='**'), name='other_studies')
    etype_class.add_relation(SubjectRelation('Device', cardinality='?*',
                                             inlined=True), name='uses_device')
# Some questionnaire run could have specific results files (subject dependant)
Questionnaire.add_relation(SubjectRelation(('File', 'FileSet', 'ExternalFile'),
                                           cardinality='**', composite='subject'),
                           name='configuration_files')
Questionnaire.add_relation(SubjectRelation('ScoreDefinition', cardinality='*?'),
                           name='definitions')
ScoreDefinition.add_relation(SubjectRelation('Question', cardinality='**'),
                             name='used_by')
AnatomicalRegion.add_relation(SubjectRelation('ScoreValue', cardinality='**'),
                              name='concerned_by')
ColumnRef.add_relation(SubjectRelation('Assessment', cardinality='1*', inlined=True,
                                       composite='object'), name='assessment')
# Measure -> Files
for etype_class in (QuestionnaireRun, Scan, GenomicMeasure, IHCMeasure):
    etype_class.add_relation(SubjectRelation(('File', 'FileSet', 'ExternalFile'),
                                             cardinality='**', composite='subject'),
                             name='results_files')
    etype_class.add_relation(SubjectRelation(('File', 'FileSet', 'ExternalFile'),
                                             cardinality='**', composite='subject'),
                             name='configuration_files')
# Extra fields for CWUser
CWUser.add_relation(String(maxsize=512, fulltextindexed=True), name='affiliation')
CWUser.add_relation(String(maxsize=512, fulltextindexed=True), name='extra_infos')
# Genomic
Gene.add_relation(SubjectRelation('Study', cardinality='**'), name=u'relevant_gene_for')
# Clinipath
Subject.add_relation(SubjectRelation(('Biopsy', 'BiopsySample', 'CellCulture', 'BloodSample'),
                                     cardinality='?*', composite='subject'),
                     name='related_samples')
GenomicMeasure.add_relation(SubjectRelation(('Biopsy', 'BiopsySample', 'CellCulture', 'BloodSample'),
                                            cardinality='**'),
                            name='measured_on_sample')
for etype_class in (Biopsy, BiopsySample, CellCulture, BloodSample):
    etype_class.add_relation(SubjectRelation('MedicalTechnique', cardinality='?*',
                                             inlined=True),
                             name='technique_type')
    etype_class.add_relation(SubjectRelation('BodyLocation', cardinality='?*'),
                             name='from_location')
    etype_class.add_relation(SubjectRelation('Study', cardinality='1*', inlined=True),
                             name='related_study')
    etype_class.add_relation(SubjectRelation('Study', cardinality='**'),
                             name='other_studies')
    etype_class.add_relation(SubjectRelation('Device', cardinality='?*', inlined=True),
                             name='uses_device')


# Comments for entities
class comments(RelationDefinition):
    subject = 'Comment'
    object = ('Scan', 'GenomicMeasure', 'QuestionnaireRun', 'IHCMeasure')
    composite='object'


# Links to "Wikis" / Cards
class wiki(RelationDefinition):
    subject = ('Question', 'Questionnaire', 'Study', 'ScoreDefinition')
    object = 'Card'
    cardinality = '**'
    composite='subject'
