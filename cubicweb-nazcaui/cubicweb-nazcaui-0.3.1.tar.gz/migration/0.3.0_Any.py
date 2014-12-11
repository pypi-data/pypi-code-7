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

drop_entity_type('NazcaAlignment')
drop_entity_type('AlignmentParameter')
drop_relation_type('alignment_parameters')
add_attribute('File', 'separator')
add_attribute('File', 'autocast')
sync_schema_props_perms('File', 'title')

add_entity_type('QueryDataSet')
add_entity_type('Distance')
add_entity_type('DistanceRun')
add_entity_type('Blocking')
add_entity_type('BlockingRun')
add_entity_type('Normalization')
add_entity_type('NormalizationRun')
add_entity_type('ParameterDefinition')
add_entity_type('ParameterPossibleValue')
add_entity_type('ParameterValue')
add_entity_type('Alignment')
add_entity_type('AlignmentResult')
