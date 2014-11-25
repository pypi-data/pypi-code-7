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

"""cubicweb-brainomics entity's classes"""
import os.path as osp

from cubicweb.view import EntityAdapter
from cubicweb.predicates import is_instance

from cubes.medicalexp.entities import ScoreValue


MEASURES = ['GenericMeasure', 'Scan', 'GenericTestRun', 'QuestionnaireRun', 'GenomicMeasure']


class AssessmentICalendarableAdapter(EntityAdapter):
    __regid__ = 'ICalendarable'
    __select__ = EntityAdapter.__select__ & is_instance('Assessment')

    @property
    def start(self):
        return self.entity.datetime

    @property
    def end(self):
        return self.entity.datetime


class DiagnosticICalendarableAdapter(EntityAdapter):
    __regid__ = 'ICalendarable'
    __select__ = EntityAdapter.__select__ & is_instance('Diagnostic')

    @property
    def start(self):
        return self.entity.diagnostic_date


class ScoreValue(ScoreValue):

    @property
    def subject(self):
        if self.reverse_related_infos:
            return self.reverse_related_infos[0]
        if self.measure:
            return self.measure[0].concerns[0]
        if self.score_of_sample:
            return self.score_of_sample[0].reverse_related_samples[0]
