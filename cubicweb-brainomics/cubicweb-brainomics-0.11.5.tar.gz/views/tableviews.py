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

"""cubicweb-brainomics views/forms/actions/components for web ui"""
from logilab.mtconverter import xml_escape
from cubicweb.selectors import is_instance
from cubicweb.web.views.tableview import (TableLayout, EntityTableView,
                                          RelationColRenderer, EntityTableColRenderer)

from cubes.brainomics.views.slickgrid import SlickGridEntityTableView

_ = unicode


class FilterTableLayout(TableLayout):
    __regid__ = 'filter_table_layout'
    display_filter = 'top'
    hide_filter = False


def render_width(w, entity):
    w(entity.genomic_region[0].width)


class AbstractCghTableView(SlickGridEntityTableView, EntityTableView):
    __abtract__ = True
    paginable = False
    __select__ = EntityTableView.__select__ & is_instance('CghResult')
    columns = ['cgh_ratio', 'log2_ratio', 'status', 'width', 'numprobes']
    column_renderers = {'width':  EntityTableColRenderer(renderfunc=render_width)}
    grid_options = {'enableCellNavigation': True, 'frozenColumn': 0}
    default_column_options = {'sortable': True, 'width': 140,}



class CghTableView(AbstractCghTableView):
    __regid__ = 'genmeas-table-view'
    columns = ['genomic_region',] + AbstractCghTableView.columns
    AbstractCghTableView.column_renderers.update({'genomic_region':
                                                  RelationColRenderer(role='subject')})



class GeneCghTableView(AbstractCghTableView):
    __regid__ = 'gene-genmeas-table-view'
    columns = ['genomic_region', 'related_measure'] + AbstractCghTableView.columns
    AbstractCghTableView.column_renderers.update({'related_measure':
                                                  RelationColRenderer(role='subject',
                                                                      vid='incontext'),
                                                  'genomic_region':
                                                  RelationColRenderer(role='subject',
                                                                      vid='incontext')})


class RegionCghTableView(AbstractCghTableView):
    __regid__ = 'region-genmeas-table-view'
    columns = ['related_measure',] + AbstractCghTableView.columns
    AbstractCghTableView.column_renderers.update({'related_measure':
                                                  RelationColRenderer(role='subject',
                                                                      vid='incontext')})


class AbstractMutationTableView(SlickGridEntityTableView, EntityTableView):
    __abstract__ = True
    paginable = False
    __select__ = EntityTableView.__select__ & is_instance('Mutation')

    columns = ['conclusions', 'position_in_gene',
               'mutation_type', 'amplicon', 'protein',
               'classification_type', 'variant_frequency',
               'reference_base', 'variant_base', 'variant_coverage', 'coverage',
               'reference_id', 'dbsnp', 'locus_version', 'nucl',
               'sift', 'polyphen', 'classification_variant']
    grid_options = {'enableCellNavigation':True, 'frozenColumn': 0}


class MutationTableView(AbstractMutationTableView):
    __regid__ = 'genmeas-table-view'
    column_renderers = {'related_gene': RelationColRenderer(role='subject', vid='incontext')}
    columns = ['related_gene',] + AbstractMutationTableView.columns


class GeneMutationTableView(AbstractMutationTableView):
    __regid__ = 'gene-genmeas-table-view'
    column_renderers = {'related_measure': RelationColRenderer(role='subject', vid='incontext')}
    columns = ['related_measure',] + AbstractMutationTableView.columns


###############################################################################
### SCORE GROUP ###############################################################
###############################################################################
class ScoreValueOutofContextTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('ScoreValue')
    __regid__ = 'scorevalue-outofcontext-table-view'

    columns = ['definition', 'text', 'value']
    column_renderers = {'definition': RelationColRenderer(role='subject')}


class ScoreValueInContextTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('ScoreValue')
    __regid__ = 'scorevalue-incontext-table-view'

    def render_value(w, entity):
        w(u'<ul>%s</ul>' % entity.complete_value)

    def render_datetime(w, entity):
        w(u'<ul>%s</ul>' % (entity.datetime or u'-'))

    def render_target(w, entity):
        w(u'%s' % entity.subject.view('incontext'))

    columns = ['subject', 'value', 'datetime']
    column_renderers = {'datetime': EntityTableColRenderer(renderfunc=render_datetime),
                        'subject': EntityTableColRenderer(renderfunc=render_target),
                        'value': EntityTableColRenderer(renderfunc=render_value)}


###############################################################################
### DRUG TAKES ################################################################
###############################################################################
class AbstractDrugTakeTableView(SlickGridEntityTableView):
    __abstract__ = True
    paginable = False
    __select__ = EntityTableView.__select__ & is_instance('DrugTake')
    grid_options = {'enableCellNavigation': True, 'frozenColumn': 0}
    default_column_options = {'sortable': True, 'width': 140,}
    columns = ['drug']
    column_renderers = {'drug': RelationColRenderer(role='subject', vid='incontext')}


class InTherapyDrugTakeTableView(AbstractDrugTakeTableView):
    __regid__ = 'intherapy-drugtake-table-view'

    columns = (AbstractDrugTakeTableView.columns +
               ['start_taking_date', 'stop_taking_date',
                'take_order', 'dosis', 'unit', 'number_of_cycles', 'dosis_percentage',
                'reduced_dosis'])


class DrugTakeTableView(AbstractDrugTakeTableView):
    __regid__ = 'drugtake-table-view'

    columns = (AbstractDrugTakeTableView.columns +
               ['taken_in_therapy', 'start_taking_date', 'stop_taking_date',
                'take_order', 'dosis', 'unit', 'number_of_cycles', 'dosis_percentage',
                'reduced_dosis'])

    column_renderers = AbstractDrugTakeTableView.column_renderers
    column_renderers['taken_in_therapy'] = RelationColRenderer(role='subject', vid='incontext')


###############################################################################
### ANSWERS ###################################################################
###############################################################################
class AnswerInContextTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('Answer')
    __regid__ = 'answer-incontext-table-view'
    columns = ['answer', 'value', 'datetime']

    def render_value(w, entity):
        w(u'%s' % entity.computed_value)

    def render_text(w, entity):
        w(u'%s' % entity.question[0].text)

    def render_answer(w, entity):
        w(u'<a href="%s">%s</a>' % (xml_escape(entity.absolute_url()),
                                    xml_escape(entity.dc_title())))

    column_renderers = {'answer': EntityTableColRenderer(renderfunc=render_answer),
                        'value': EntityTableColRenderer(renderfunc=render_value)}


class AnswerOutOfContextTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('Answer')
    __regid__ = 'answer-outofcontext-table-view'
    columns = ['question', 'text', 'value', 'datetime']

    def render_text(w, entity):
        w(u'%s' % entity.question[0].text)

    def render_question(w, entity):
        entity = entity.question[0]
        w(u'<a href="%s">%s</a>' % (xml_escape(entity.absolute_url()),
                                    xml_escape(entity.dc_title())))

    column_renderers = {'question': EntityTableColRenderer(renderfunc=render_question),
                        'text': EntityTableColRenderer(renderfunc=render_text)}


###############################################################################
### QUESTIONS #################################################################
###############################################################################
class QuestionTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('Question')
    __regid__ = 'question-table-view'
    columns = ['question', 'text', 'type', 'possible_answers', 'answers']

    def render_question(w, entity):
        w(u'%s'% xml_escape(entity.dc_title()))

    def render_answers(w, entity):
        w(u'<a href="%s">%s</a>' % (xml_escape(entity.absolute_url()),
                                    _('See detailed question')))

    column_renderers = {'question': EntityTableColRenderer(renderfunc=render_question),
                        'answers': EntityTableColRenderer(renderfunc=render_answers)}


###############################################################################
### DIAGNOSTIC/ANALYSIS #######################################################
###############################################################################
class DiagnosticsTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('Diagnostic')
    __regid__ = 'diagnostics-table-view'

    columns = ['diagnostic_date', 'conclusion', 'diagnostic_location',
               'diagnosed_disease', 'based_on']
    column_renderers = {'diagnostic_location': RelationColRenderer(role='subject', vid='incontext'),
                        'diagnosed_disease': RelationColRenderer(role='subject', vid='incontext'),
                        'technique_type': RelationColRenderer(role='subject', vid='incontext'),
                        'based_on': RelationColRenderer(role='subject', vid='incontext'),
                       }


class TechnicalAnalysisTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('TechnicalAnalysis')
    __regid__ = 'analysis-table-view'

    def render_analysis_on(w, entity):
        if entity.performed_on:
            return entity.performed_on[0].view('incontext')
        elif entity.analysis_of_sample:
            return entity.analysis_of_sample[0].view('incontext')

    columns = ['technique_type', 'results', 'conclusion',
               'analysis_date', _('analysis_on')]
    column_renderers = {'technique_type': RelationColRenderer(role='subject', vid='incontext'),
                        'analysis_on': EntityTableColRenderer(renderfunc=render_analysis_on)
                       }


###############################################################################
### CLINIPATH #################################################################
###############################################################################
class BiopsySampleTableView(EntityTableView):
    __select__ = EntityTableView.__select__ & is_instance('BiopsySample')
    __regid__ = 'biopsysample-table-view'
    layout_id = 'table_layout'
    columns = ['size', 'name', 'code', 'tumoral_cell_percent', 'necrosis_percent']
