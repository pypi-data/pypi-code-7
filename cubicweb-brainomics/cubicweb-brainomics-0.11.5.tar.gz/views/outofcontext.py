# -*- coding: utf-8 -*-
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2014 CEA (Saclay, FRANCE), all rights reserved.
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
from cubicweb.predicates import is_instance
from cubicweb.view import EntityView


class BrainomicsAbstractOutOfContextView(EntityView):
    __regid__ = 'outofcontext'
    __abstract__ = True
    icon = None
    local_image = None
    css_class = None

    def add_icon(self):
        if self.icon:
            icon = u'<span class="glyphicon glyphicon-%s"></span>' % self.icon
        elif self.local_image:
            image = u'<img alt="" src="%s">' %  self._cw.data_url(self.local_image)
        else:
            icon = u''
        self.w(u'<div class="col-md-2"><p class="text-center">%s</p></div>' % icon)

    def additional_infos(self, entity):
        pass

    def cell_call(self, row, col):
        w = self.w
        entity = self.cw_rset.get_entity(row, col)
        klass = [u'ooview']
        if self.css_class is not None:
            klass.append(self.css_class)
        klass = ' '.join(klass)
        w(u'<div class="%s"><div class="well"><div class="row">' % klass)
        self.add_icon()
        w(u'<div class="col-md-10"><h4>%s</h4></div>' % entity.view('incontext'))
        w(u'</div>')
        self.additional_infos(entity)
        w(u'</div></div>')


class StudyOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Study')
    icon = 'folder-open'


class SubjectOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Subject')
    icon = 'user'


class AssessmentOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Assessment')
    icon = 'time'


class GenomicMeasureOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('GenomicMeasure')
    icon = 'filter'


class GeneContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Gene')
    icon = 'link'


class GenomicRegionContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('GenomicRegion')
    icon = 'pushpin'


class ScanOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Scan')
    icon = 'film'


class QuestionnaireOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Questionnaire')
    icon = 'list'


class QuestionnaireRunOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('QuestionnaireRun')
    icon = 'list-alt'


class AnswerOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Answer')
    icon = 'info-sign'


class QuestionContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Question')
    icon = 'question-sign'


class ScoreDefinitionOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('ScoreDefinition')
    icon = 'tags'


class ScoreValueOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('ScoreValue')
    icon = 'tag'


class TherapyOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Therapy')
    icon = 'ok-sign'


class DiagnosticOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Diagnostic')
    icon = 'comment'


class CenterOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Center')
    icon = 'home'


class MedicalTechniqueOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('MedicalTechnique')
    icon = 'cog'


class DiseaseOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Disease')
    icon = 'certificate'


class BodyLocationOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('BodyLocation')
    icon = 'heart-empty'


class DrugContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Drug')
    icon = 'tint'

class DrugTakeContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('DrugTake')
    icon = 'calendar'


class FileOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('ExternalFile', 'File')
    icon = 'file'


class FileSetOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('FileSet')
    icon = 'folder-close'


class GenericTestRunOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('GenericTestRun')
    icon = 'wrench'


class BiologicalSamplesOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('Biopsy',
                                                                             'BiopsySample',
                                                                             'CellCulture',
                                                                             'BloodSample')
    icon = 'asterisk'


class TherapyEvaluationOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('TherapyEvaluation')
    icon = 'info-sign'


class SurvivalDataOutOfContextView(BrainomicsAbstractOutOfContextView):
    __select__ = BrainomicsAbstractOutOfContextView.__select__ & is_instance('SurvivalData')
    icon = 'heart'
