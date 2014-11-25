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
import warnings

from cubicweb.web import facet
from cubicweb.predicates import is_instance
try:
    from cubicweb.web.facet import AbstractRangeRQLPathFacet
    warnings.warn('AbstractRangeRQLPathFacet are now available. '
                  'The file cubes.brainomics.views.rqlpathfacets should be removed')
except ImportError:
    from cubes.brainomics.views.rqlpathfacets import AbstractRangeRQLPathFacet
    warnings.warn('AbstractRangeRQLPathFacet are backport from CW 3.19')


_ = unicode


def translatable(value):
    @property
    def translate(self, value=value):
        return self._cw._(value).capitalize()
    return translate


class SubjectAgeFacet(AbstractRangeRQLPathFacet, facet.RangeFacet):
    __regid__ = 'subject-age-facet'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Subject')
    path = ['A admission_of X', 'A subject_age V']
    order = 3
    filter_variable = 'V'
    title = translatable(_('Age'))


class MeasureAgeFacet(facet.RQLPathFacet):
    __regid__ = 'measure-age-facet'
    __select__ = is_instance('Scan', 'QuestionnaireRun', 'GenomicMeasure')
    path = ['S generates X', 'S age_of_subject A']
    order = 1
    filter_variable = 'A'
    title = translatable(_("Subject Age"))


class MeasureHandednessFacet(facet.RQLPathFacet):
    __regid__ = 'measure-handedness-facet'
    __select__ = is_instance('Scan', 'QuestionnaireRun', 'GenomicMeasure')
    path = ['X concerns S', 'S handedness H']
    order = 2
    filter_variable = 'H'
    title = translatable(_('Subject Handedness'))


class MeasureGenderFacet(facet.RQLPathFacet):
    __regid__ = 'measure-gender-facet'
    __select__ = is_instance('Scan', 'QuestionnaireRun', 'GenomicMeasure')
    path = ['X concerns S', 'S gender G']
    order = 3
    filter_variable = 'G'
    title = translatable(_('Subject Gender'))


class BiopsyTissueTypeFacet(facet.AttributeFacet):
    __regid__ = 'biopsy-tissuetype-facet'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Biopsy')
    rtype = 'tissue_type'
    title = translatable(_('tissue_type'))


class BiopsyDatetimeFacet(facet.DateRangeFacet):
    __regid__ = 'biopsy-datetime'
    __select__ = facet.DateRangeFacet.__select__ & is_instance('Biopsy')
    rtype = 'biopsy_date'
    title = translatable(_('biopsy_date'))


class BiopsyDiagnosticLocation(facet.RQLPathFacet):
    __regid__ = 'biopsy-diagnostic-location'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Biopsy')
    path = ['S based_on X', 'S diagnostic_location L', 'L name N']
    filter_variable = 'N'
    order = 3
    title = translatable(_('diagnostic_location'))


class BiopsyDiagnosticDisease(facet.RQLPathFacet):
    __regid__ = 'biopsy-diagnostic-disease'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Biopsy')
    path = ['S based_on X', 'S diagnosed_disease L', 'L name N']
    filter_variable = 'N'
    order = 2
    title = translatable(_('diagnosed_disease'))


class BiopsyDiagnosticTechniqueType(facet.RQLPathFacet):
    __regid__ = 'biopsy-diagnostic-technique'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Biopsy')
    path = ['S based_on X', 'S technique_type L', 'L name N']
    filter_variable = 'N'
    title = translatable(_('TechniqueType'))


class BiopsySampleCellularityAgeFacet(AbstractRangeRQLPathFacet, facet.RangeFacet):
    __regid__ = 'biopsysample-cellularity-facet'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Biopsy')
    path = ['B extracted_from X', 'B tumoral_cell_percent T']
    order = 1
    filter_variable = 'T'
    title = translatable(_('tumoral_cell_percent'))


class GenomicMeasureType(facet.AttributeFacet):
    __regid__ = 'genomic-measure-type'
    __select__ = facet.AttributeFacet.__select__ & is_instance('GenomicMeasure')
    rtype = 'type'
    order = 1


class BodyLocationBiospyFacet(facet.HasRelationFacet):
    __regid__ = 'bodylocation-biopsy-facet'
    __select__ = facet.HasRelationFacet.__select__ & is_instance('BodyLocation')
    rtype = 'location_on_body'
    role = 'object'
    title = translatable(_('location_on_body'))


class TechniqueTypeBiospyFacet(facet.HasRelationFacet):
    __regid__ = 'techniquetype-biopsy-facet'
    __select__ = facet.HasRelationFacet.__select__ & is_instance('TechniqueType')
    rtype = 'technique_type'
    role = 'object'
    title = translatable(_('technique_type'))


class DiseaseBiospyFacet(facet.HasRelationFacet):
    __regid__ = 'disease-biopsy-facet'
    __select__ = facet.HasRelationFacet.__select__ & is_instance('Disease')
    rtype = 'lesion'
    role = 'object'
    title = translatable(_('lesion'))
