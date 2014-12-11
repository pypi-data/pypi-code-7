# -*- coding: utf-8 -*-
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

"""cubicweb-nazcaui schema"""

from yams.buildobjs import (EntityType, SubjectRelation,
                            String, Int, Float, Date, Boolean)

from cubicweb.schema import RQLConstraint

from cubes.file.schema import File


File.add_relation(String(required=True, maxsize=8), name='separator')
File.add_relation(Boolean(default=False), name='autocast')
File.get_relation('title').cardinality = '1*'


class QueryDataSet(EntityType):
    title = String(required=True, unique=True, maxsize=256)
    datatype = String(required=True, vocabulary=('rql', 'sparql'))
    source = String(required=True, maxsize=128)
    query = String(required=True)
    autocast = Boolean(default=False)
    cache_result = Boolean(default=False)
    cache_result_file = SubjectRelation('File', cardinality='?*', inlined=True)


class Distance(EntityType):
    name = String(required=True, unique=True, maxsize=256)
    parameters = SubjectRelation('ParameterDefinition', cardinality='*1')


class DistanceRun(EntityType):
    function = SubjectRelation('Distance', cardinality='1*', inlined=True)
    parameters = SubjectRelation('ParameterValue', cardinality='**')
    refset_index = Int(required=True)
    targetset_index = Int(required=True)
    weight = Float(required=True, default=1.)


class Blocking(EntityType):
    name = String(required=True, unique=True, maxsize=256)
    parameters = SubjectRelation('ParameterDefinition', cardinality='*1')


class BlockingRun(EntityType):
    function = SubjectRelation('Blocking', cardinality='1*', inlined=True)
    parameters = SubjectRelation('ParameterValue', cardinality='**')
    refset_index = Int(required=True)
    targetset_index = Int(required=True)
    order = Int()


class Normalization(EntityType):
    name = String(required=True, unique=True, maxsize=256)
    parameters = SubjectRelation('ParameterDefinition', cardinality='*1')


class NormalizationRun(EntityType):
    function = SubjectRelation('Normalization', cardinality='1*', inlined=True)
    parameters = SubjectRelation('ParameterValue', cardinality='**')
    index = Int(required=True)
    order = Int()


class ParameterDefinition(EntityType):
    name = String(maxsize=256, required=True)
    value_type = String(required=True, maxsize=256)
    description = String()
    possible_values = SubjectRelation('ParameterPossibleValue', cardinality='**')


class ParameterPossibleValue(EntityType):
    value = String(required=True, maxsize=256)


class ParameterValue(EntityType):
    value_of = SubjectRelation('ParameterDefinition', cardinality='1*', inlined=True,
                               constraints=[RQLConstraint('D parameters O, '
                                                          'R function D, R parameters S',
                                                          msg=_('parameter not allowed '
                                                                'for this function')),])
    value = String(required=True, maxsize=256)


class Alignment(EntityType):
    name = String(required=True, maxsize=256)
    description = String()
    threshold = Float(required=True, default=0.4)
    reference_set = SubjectRelation(('File', 'QueryDataSet'), cardinality='1*', inlined=True)
    target_set = SubjectRelation(('File', 'QueryDataSet'), cardinality='1*', inlined=True)
    ref_normalizers = SubjectRelation('NormalizationRun', cardinality='*?')
    target_normalizers = SubjectRelation('NormalizationRun', cardinality='*?')
    processings = SubjectRelation('DistanceRun', cardinality='+*')
    blockings = SubjectRelation('BlockingRun', cardinality='**')
    results = SubjectRelation('AlignmentResult', cardinality='*?')


class AlignmentResult(EntityType):
    runtime = Int()
    launch_date = Date()
    result_file = SubjectRelation('File', cardinality='1*', inlined=True)


class AlignmentThresholdedResult(EntityType):
    threshold = Float(required=True)
    result = SubjectRelation('AlignmentResult', cardinality='1*', inlined=True)
    result_file = SubjectRelation('File', cardinality='1*', inlined=True)
    reference_set_file = SubjectRelation('File', cardinality='1*', inlined=True)
    target_set_file = SubjectRelation('File', cardinality='1*', inlined=True)
