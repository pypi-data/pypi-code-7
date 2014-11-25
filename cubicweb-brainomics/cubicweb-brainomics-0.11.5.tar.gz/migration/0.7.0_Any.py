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

sync_schema_props_perms(('QuestionnaireRun', 'concerns', 'Subject'))
sync_schema_props_perms(('QuestionnaireRun', 'concerns', 'SubjectGroup'))

sync_schema_props_perms(('Scan', 'concerns', 'Subject'))
sync_schema_props_perms(('Scan', 'concerns', 'SubjectGroup'))

sync_schema_props_perms(('GenomicMeasure', 'concerns', 'Subject'))
sync_schema_props_perms(('GenomicMeasure', 'concerns', 'SubjectGroup'))

sync_schema_props_perms(('Assessment', 'generates', 'QuestionnaireRun'))
sync_schema_props_perms(('Assessment', 'generates', 'Scan'))
sync_schema_props_perms(('Assessment', 'generates', 'GenomicMeasure'))

sync_schema_props_perms(('ScoreValue', 'measure', 'QuestionnaireRun'))
sync_schema_props_perms(('ScoreValue', 'measure', 'Scan'))
sync_schema_props_perms(('ScoreValue', 'measure', 'GenomicMeasure'))

sync_schema_props_perms(('QuestionnaireRun', 'related_study', 'Study'))
sync_schema_props_perms(('Scan', 'related_study', 'Study'))
sync_schema_props_perms(('GenomicMeasure', 'related_study', 'Study'))

sync_schema_props_perms('external_resources')

sync_schema_props_perms(('ColumnRef', 'assessment', 'Assessment'))

sync_schema_props_perms('comments')
sync_schema_props_perms('wiki')
