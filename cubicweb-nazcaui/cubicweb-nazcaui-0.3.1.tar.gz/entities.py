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

"""cubicweb-nazcaui entity's classes"""

import re
from StringIO import StringIO

from cubicweb import Binary
from cubicweb.entities import AnyEntity

from cubes.file.entities import File

import nazca.utils.dataio as nio
import nazca.utils.distances as ndi
import nazca.utils.normalize as ndn
import nazca.rl.blocking as nrlb
import nazca.rl.aligner as nrla


def convert_value(value, value_type):
    """ Convert a value to the correct type
    """
    try:
        if value_type == 'Int':
            return int(value)
        if value_type == 'Float':
            return float(value)
        if value_type == 'Boolean':
            return bool(value_type)
        if value_type == 'Regexp':
            return re.compile(value)
    except:
        raise TypeError('Uncorrect cast of %s to %s' % (value, value_type))
    return value


def build_nazca_object(module, processing, *args, **kwargs):
    """ Build a nazca object"""
    function = processing.function[0]
    klass = getattr(module, function.name)
    if not klass:
        raise ValueError('Function %s is unknown' % function.name)
    # Additionnal parameters
    for p in processing.parameters:
        kwargs[p.value_of[0].name] = p.converted_value
    return klass(*args, **kwargs)


class File(File):

    def dc_title(self):
        return self.title

    def build_dataset(self, force_autocast=None):
        delimiter = str(self.separator)
        delimiter = '\t' if delimiter == 'tab' else delimiter
        autocast = force_autocast if force_autocast is not None else self.autocast
        return nio.parsefile(StringIO(self.data.getvalue()),
                             delimiter=delimiter,
                             autocast_data=autocast)


class QueryDataSet(AnyEntity):
    __regid__ = 'QueryDataSet'

    def build_dataset(self, force_autocast=None):
        autocast = force_autocast if force_autocast is not None else self.autocast
        # Cached and cache file
        if self.cache_result and self.cache_result_file:
            return self.cache_result_file[0].build_dataset(force_autocast=force_autocast)
        # No cache
        if not self.cache_result:
            if self.datatype == 'sparql':
                return nio.sparqlquery(self.source, self.query, autocast_data=autocast)
            else: # rql
                return nio.rqlquery(self.source, self.query, autocast_data=autocast)
        # Cache result
        if self.cache_result:
            # Do NOT autocast data for easier file creation
            if self.datatype == 'sparql':
                dataset = nio.sparqlquery(self.source, self.query, autocast_data=False)
            else: # rql
                dataset = nio.rqlquery(self.source, self.query, autocast_data=False)
            data = Binary('\n'.join('\t'.join(row) for row in dataset).encode('utf-8'))
            name = u'cache_file_%s' % self.eid
            _file = self._cw.create_entity('File',
                                           autocast=autocast,
                                           title=name,
                                           data_name=name,
                                           separator=u'\t',
                                           data_format=u"text/plain",
                                           data=data)
            self.cw_set(cache_result_file=_file)
            # XXX Better solution ?
            return _file.build_dataset(force_autocast)


class ParameterValue(AnyEntity):
    __regid__ = 'ParameterValue'

    def dc_title(self):
        return '%s = %s' % (self.value_of[0].dc_title(), self.value)

    @property
    def converted_value(self):
        value_type = self.value_of[0].value_type
        return convert_value(self.value, value_type)


class Alignment(AnyEntity):
    __regid__ = 'Alignment'

    @property
    def processings_run(self):
        """ Build the processings """
        run = []
        for processing in self.processings:
            kwargs = {'ref_attr_index': processing.refset_index,
                      'target_attr_index': processing.targetset_index,
                      'weight': processing.weight}
            run.append(build_nazca_object(ndi, processing, **kwargs))
        return run

    def _build_normalizer(self, normalizer):
        """ Build a normalizer """
        if not normalizer:
            return
        kwargs = {'attr_index': normalizer.index}
        return build_nazca_object(ndn, normalizer, **kwargs)

    def _build_pipeline_or_process(self, klass, processings):
        if len(processings)>1 and len([c for c in processings if c[1] is None]):
            raise RuntimeError('More than one processing should be ordered')
        if processings:
            if len(processings)>1:
                processing = klass([b[0] for b in sorted(processings, key=lambda x: x[1])])
            else:
                processing = processings[0][0]
        else:
            processing = None
        return processing

    @property
    def normalizers_run(self):
        """ Build the normalizers """
        ref_normalizers = [(self._build_normalizer(p), p.order) for p in self.ref_normalizers]
        target_normalizers = [(self._build_normalizer(p), p.order) for p in self.target_normalizers]
        ref = self._build_pipeline_or_process(ndn.NormalizerPipeline, ref_normalizers)
        target = self._build_pipeline_or_process(ndn.NormalizerPipeline, target_normalizers)
        return ref, target

    @property
    def blocking_run(self):
        """ Build the blockings """
        blockings = []
        for processing in self.blockings:
            kwargs = {'ref_attr_index': processing.refset_index,
                      'target_attr_index': processing.targetset_index}
            blockings.append((build_nazca_object(nrlb, processing, **kwargs), processing.order))
        return self._build_pipeline_or_process(nrlb.PipelineBlocking, blockings)

    def build_alignment(self):
        """ Build the alignment object """
        processings = self.processings_run
        ref_normalizer, target_normalizer = self.normalizers_run
        blocking = self.blocking_run
        threshold = self.threshold
        aligner = nrla.BaseAligner(threshold=threshold,
                                   processings=processings)
        if ref_normalizer:
            aligner.register_ref_normalizer(ref_normalizer)
        if target_normalizer:
            aligner.register_target_normalizer(target_normalizer)
        if blocking:
            aligner.register_blocking(blocking)
        return aligner

    def get_aligned_pairs(self):
        """ Run the alignment and get the aligned pairs """
        aligner = self.build_alignment()
        reference_set = self.reference_set[0].build_dataset()
        target_set = self.target_set[0].build_dataset()
        return list(aligner.get_aligned_pairs(reference_set, target_set))


class DistanceRun(AnyEntity):
    __regid__ = 'DistanceRun'

    def dc_title(self):
        return '%s (%s/%s/%s)' % (self.function[0].dc_title(),
                                  self.refset_index, self.targetset_index, self.weight)


class NormalizationRun(AnyEntity):
    __regid__ = 'NormalizationRun'

    def dc_title(self):
        return '%s (index %s)' % (self.function[0].dc_title(), self.index)


class BlockingRun(AnyEntity):
    __regid__ = 'BlockingRun'

    def dc_title(self):
        return '%s (%s/%s)' % (self.function[0].dc_title(),
                               self.refset_index, self.targetset_index)


class AlignmentResult(AnyEntity):
    __regid__ = 'AlignmentResult'

    def dc_title(self):
        return '%s %s (%s)' % (self._cw._('Result of'),
                               self.reverse_results[0].dc_title(),
                               self.launch_date)
