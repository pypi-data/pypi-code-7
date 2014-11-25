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

add_relation_definition('TechnicalAnalysis', 'performed_on', 'QuestionnaireRun')
add_relation_definition('TechnicalAnalysis', 'performed_on', 'Scan')
add_relation_definition('TechnicalAnalysis', 'performed_on', 'GenomicMeasure')


drop_relation_definition('Questionnaire', 'external_resources', 'ExternalResource')
add_relation_definition('Questionnaire', 'configuration_files', ('File', 'FileSet', 'ExternalFile'))

drop_relation_definition('QuestionnaireRun', 'external_resources', 'ExternalResource')
add_relation_definition('QuestionnaireRun', 'results_file', ('File', 'FileSet', 'ExternalFile'))
add_relation_definition('QuestionnaireRun', 'configuration_files', ('File', 'FileSet', 'ExternalFile'))

drop_relation_definition('Scan', 'external_resources', 'ExternalResource')
add_relation_definition('Scan', 'results_file', ('File', 'FileSet', 'ExternalFile'))
add_relation_definition('Scan', 'configuration_files', ('File', 'FileSet', 'ExternalFile'))

drop_relation_definition('GenomicMeasure', 'external_resources', 'ExternalResource')
add_relation_definition('GenomicMeasure', 'results_file', ('File', 'FileSet', 'ExternalFile'))
add_relation_definition('GenomicMeasure', 'configuration_files', ('File', 'FileSet', 'ExternalFile'))

remove_cube('file')

sync_schema_props_perms('concerns')
sync_schema_props_perms('uses')
sync_schema_props_perms('comments')
add_relation_definition('Diagnostic', 'based_on', 'QuestionnaireRun')
add_relation_definition('Diagnostic', 'based_on', 'Scan')
add_relation_definition('Diagnostic', 'based_on', 'GenomicMeasure')
sync_schema_props_perms(('Diagnostic', 'based_on', 'QuestionnaireRun'))
sync_schema_props_perms(('Diagnostic', 'based_on', 'Scan'))
sync_schema_props_perms(('Diagnostic', 'based_on', 'GenomicMeasure'))
