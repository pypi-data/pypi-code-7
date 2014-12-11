# -*- coding: utf-8 -*-
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-nazcaui views"""

from datetime import datetime
from logilab.common.date import ustrftime

from rdflib import Namespace as RdfNamespace, Graph as RdfGraph, URIRef

from cubicweb import Binary
from cubicweb.predicates import is_instance, anonymous_user, one_line_rset
from cubicweb.web.action import Action
from cubicweb.view import EntityView
from cubicweb.web import uihelper
from cubicweb.web.views import uicfg
from cubicweb.web.views.json import JsonMixIn
from cubicweb.web.views.csvexport import CSVMixIn
from cubicweb.web.views.startup import IndexView
from cubicweb.web import facet as facetbase
from cubicweb.web import formfields as ff, Redirect, ValidationError
import cubicweb.web.formwidgets as fwdgs
from cubicweb.web.views.basecontrollers import Controller
from cubicweb.web.views import forms


_ = unicode


RDF = RdfNamespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
CW = RdfNamespace('http://ns.cubicweb.org/cubicweb/0.0/')
OWL = RdfNamespace('http://www.w3.org/2002/07/owl#')


#UICFG/UIHELPER
_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl
_pvs.tag_object_of(('Alignment', 'reference_set', '*'), 'relations')
_pvs.tag_object_of(('Alignment', 'target_set', '*'), 'relations')
_pvs.tag_subject_of(('Alignment', 'results', '*'), 'relations')
_pvs.tag_subject_of(('Alignment', 'ref_normalizers', '*'), 'attributes')
_pvs.tag_subject_of(('Alignment', 'target_normalizers', '*'), 'attributes')
_pvs.tag_subject_of(('Alignment', 'blockings', 'BlockingRun'), 'attributes')
_pvs.tag_object_of(('Alignment', 'blockings', 'BlockingRun'), 'attributes')
_pvs.tag_object_of(('Alignment', 'results', 'AlignmentResult'), 'attributes')
_pvs.tag_object_of(('AlignmentResult', 'result_file', 'File'), 'attributes')
_pvs.tag_subject_of(('QueryDataSet', 'cache_result_file', 'File'), 'attributes')
_pvs.tag_subject_of(('*', 'parameters', 'ParameterValue'), 'attributes')
_pvs.tag_object_of(('*', 'cache_result_file', 'File'), 'attributes')


uihelper.edit_inline('DistanceRun', 'parameters')
uihelper.edit_inline('NormalizationRun', 'parameters')
uihelper.edit_inline('BlockingRun', 'parameters')
uihelper.edit_inline('Alignment', 'processings')
uihelper.edit_inline('Alignment', 'blockings')
uihelper.edit_inline('Alignment', 'ref_normalizers')
uihelper.edit_inline('Alignment', 'target_normalizers')
uihelper.set_field_kwargs('Alignment', 'ref_normalizers', label=_('ref_normalizers'))
uihelper.set_field_kwargs('Alignment', 'target_normalizers', label=_('target_normalizers'))


### VIEWS
class LaunchAlignmentView(EntityView):
    __select__ = EntityView.__select__ & is_instance('Alignment') & ~anonymous_user()
    __regid__ = 'launch-alignment'

    def entity_call(self, entity):
        pairs = entity.get_aligned_pairs()
        # Create a result file
        data = Binary('\n'.join('%s\t%s\t%s\t%s\t%s' % (p[0][0].encode('utf-8'), str(p[0][1]),
                                                        p[1][0].encode('utf-8'), str(p[1][1]),
                                                        p[2]) for p in pairs))
        now = datetime.now()
        name = u'results_%s' % ustrftime(now, u'%Y-%m-%d %H:%M:%S')
        file = self._cw.create_entity('File',
                                      title=name,
                                      data_name=name,
                                      separator=u'\t',
                                      data_format=u"text/plain",
                                      data=data)
        res = self._cw.create_entity('AlignmentResult',
                                     result_file=file,
                                     launch_date=now,
                                     reverse_results=entity.eid)
        self.w(u'<h2>%s</h2>' % self._cw._('The alignment is done'))
        self.w(u'<a href="%s">%s</a>' % (res.absolute_url(), self._cw._('See the results')))


class FileHTMLResultView(EntityView):
    __select__ = EntityView.__select__ & is_instance('File', 'QueryDataSet')
    __regid__ = 'html-results'

    def get_data(self, entity):
        return entity.build_dataset()

    def entity_call(self, entity):
        data = self.get_data(entity)
        self.w(u'<table class="table table-condensed table-bordered table-hover">')
        self.w(u'<thead><tr><td colspan="%s">The Results</td></tr></thead>'
               % len(data))
        self.w(u'<tbody>')
        for line in data:
            for elt in line:
                elt = elt.decode('utf-8')
                if isinstance(elt, basestring) and (elt.startswith('http://') or
                                                    elt.startswith('www.')):
                    self.w(u'<td><a href="%(e)s">%(e)s</a></td>'
                           % {'e': _(elt)})
                else:
                    self.w(u'<td>%s</td>' % _(elt))
            self.w(u'</tr>')
        self.w(u'</tbody>')
        self.w(u'</table>')


class HTMLResultView(FileHTMLResultView):
    __select__ = EntityView.__select__ & is_instance('AlignmentResult')

    def get_data(self, entity):
        return entity.result_file[0].build_dataset()


class JsonResultsView(JsonMixIn, EntityView):
    __select__ = EntityView.__select__ & is_instance('AlignmentResult')
    __regid__ = 'json-results'

    def entity_call(self, entity):
        data = entity.result_file[0].build_dataset()
        self.wdata(data)


class RdfResultsView(CSVMixIn, EntityView):
    __select__ = EntityView.__select__ & is_instance('AlignmentResult')
    __regid__ = 'rdf-results'

    def entity_call(self, entity):
        data = entity.result_file[0].build_dataset()
        graph = RdfGraph()
        graph.bind('cw', CW)
        graph.bind('owl', OWL)
        for line in data:
            if line[-1] == 'not_found':
                continue
            graph.add( (URIRef(line[0]), OWL.sameAs, URIRef(line[1])) )
        self.w(graph.serialize().decode('utf-8'))


### ACTIONS
class AddQueryDatasetAction(Action):
    __regid__ = 'add-query-dataset'
    __select__ = Action.__select__ & ~anonymous_user()
    title = _('Add query dataset')
    category = 'add-actions'
    order = 1

    def url(self):
        return self._cw.build_url('add/QueryDataSet')


class AddFileAction(Action):
    __regid__ = 'add-file-dataset'
    __select__ = Action.__select__ & ~anonymous_user()
    title = _('Add file dataset')
    category = 'add-actions'
    order = 1

    def url(self):
        return self._cw.build_url('add/File')


class AddAlignmentAction(Action):
    __regid__ = 'add-alignment'
    __select__ = Action.__select__ & ~anonymous_user()
    title = _('Add alignment')
    category = 'add-actions'
    order = 1

    def url(self):
        return self._cw.build_url('add/Alignment')


class LaunchAlignmentAction(Action):
    __regid__ = 'launch-alignment'
    __select__ = Action.__select__ & is_instance('Alignment') & ~anonymous_user()
    title = _('launch alignment')
    category = 'mainactions'
    order = 1

    def url(self):
        return self._cw.build_url(vid='launch-alignment')


class HTMLResultAction(Action):
    __regid__ = 'result-html'
    __select__ = (Action.__select__ & is_instance('AlignmentResult', 'File', 'QueryDataSet')
                  & one_line_rset())
    title = _('See in browser')
    category = 'mainactions'

    def url(self):
        return self._cw.build_url(vid='html-results')


class JSONResultAction(Action):
    __regid__ = 'result-json'
    __select__ = Action.__select__ & is_instance('AlignmentResult') & one_line_rset()
    title = _('See as json')
    category = 'mainactions'

    def url(self):
        return self._cw.build_url(vid='json-results')


class RDFResultAction(Action):
    __regid__ = 'result-rdf'
    __select__ = Action.__select__ & is_instance('AlignmentResult') & one_line_rset()
    title = _('See as rdf')
    category = 'mainactions'

    def url(self):
        return self._cw.build_url(vid='rdf-results')


class FilterResultAction(Action):
    __regid__ = 'filter-result'
    __select__ = Action.__select__ & is_instance('AlignmentResult') & one_line_rset()
    title = _('Build dataset from result')
    category = 'mainactions'

    def url(self):
        return self._cw.build_url(vid='filter-result')


# FORMS AND CONTROLLES
class FilterResultView(EntityView):
    __regid__ = 'filter-result'
    __select__ = EntityView.__select__ & is_instance('AlignmentResult') & one_line_rset()

    def call(self):
        self.w(u'<div class="col-md-12">')
        self.w(u'<h2>%s</h2>' % self._cw._('Filter the result'))
        self.w(u'<div class="well">%s</div>'
               % self._cw._('Choose a threshold. Results below this threshold will '
                            'be kept in results file, results above the threshold will be used '
                            'to create dataset files.'))
        entities_form = self._cw.vreg['forms'].select('filter-result-form',
                                                      self._cw, rset=self.cw_rset)
        entities_form.render(w=self.w)
        self.w(u'</div>')


class FilterResultForm(forms.EntityFieldsForm):
    __regid__ = 'filter-result-form'
    form_buttons = [fwdgs.SubmitButton(label=_('Validate'), attrs={"class": "btn btn-primary"})]
    threshold = ff.FloatField(name='__threshold',
                              required=True,
                              label=_('Threshold for validated results'),
                              order=1,)

    @property
    def action(self):
        return self._cw.build_url('filter-result-controller')


class FilterResultController(Controller):
    __regid__ = 'filter-result-controller'

    def _build_thresholded_dataset(self, uris, dataset, name):
        data = []
        for row in dataset.build_dataset(force_autocast=False):
            if row[0] in uris:
                data.append('\t'.join(row))
        d = '\n'.join(data)
        if isinstance(d, unicode):
            d = d.encode('utf-8')
        return self._cw.create_entity('File', title=name, data_name=name,
                                      data=Binary(d),
                                      separator=u'\t', data_format=u"text/plain")

    def publish(self, rset=None):
        threshold = float(self._cw.form['__threshold'])
        alignment_result = self._cw.entity_from_eid(self._cw.form['eid'])
        # Filter result
        reference_set_id, target_set_id, result_th  = set(), set(), []
        data_file = alignment_result.result_file[0]
        for row in data_file.build_dataset():
            if float(row[4])<=threshold:
                result_th.append('\t'.join(row))
            else:
                reference_set_id.add(row[0])
                target_set_id.add(row[2])
        # Build result file
        data = Binary('\n'.join(result_th))
        name = data_file.title + '_thresholded_' + str(threshold)
        result_th = self._cw.create_entity('File', title=name, data_name=name, data=data,
                                      separator=u'\t', data_format=u"text/plain")
        # Build thresholded datasets
        name = data_file.title + '_thresholded_' + str(threshold) + '_ref_set'
        refset = alignment_result.reverse_results[0].reference_set[0]
        refset = self._build_thresholded_dataset(reference_set_id, refset, name)
        name = data_file.title + '_thresholded_' + str(threshold) + '_target_set'
        targetset = alignment_result.reverse_results[0].target_set[0]
        targetset = self._build_thresholded_dataset(target_set_id, targetset, name)
        res = self._cw.create_entity('AlignmentThresholdedResult',
                                     threshold=threshold,
                                     result=alignment_result,
                                     result_file=result_th,
                                     reference_set_file=refset,
                                     target_set_file=targetset)
        raise Redirect(res.absolute_url())



### STARTUP VIEW
class NazcaIndexView(IndexView):

    def _build_panel(self, title, rql):
        w = self.w
        w(u'<div class="col-md-4">')
        w(u'<div class="panel panel-primary">')
        w(u'<div class="panel-heading"><h3 class="panel-title">%s</h3></div>' % title)
        rset = self._cw.execute(rql).limit(5)
        url = self._cw.build_url(rql=rql)
        w(u'<div class="panel-body">')
        if rset:
            w(self._cw.view('list', rset=rset))
            w(u'<p class="text-center">')
            w(u'<a class="btn btn-primary active" href="%s">%s</a>'
              % (url, self._cw._('See all')))
            w(u'</p>')
        else:
            w(self._cw._('No data for now'))
        w(u'</div>')
        w(u'</div>')
        w(u'</div>')


    def call(self, **kwargs):
        w = self.w
        # Card
        card = self._cw.execute('Any X WHERE X is Card, X title "index"')
        if card:
            w(card.get_entity(0, 0).content)
        # Actions
        possible_actions = self._cw.vreg['actions'].possible_actions(self._cw)
        w(u'<div class="well">')
        w(u'<p class="text-center">')
        for link in list(possible_actions.get('add-actions', [])):
            w(u'<a class="btn btn-success active" href="%s">%s</a>'
              %  (link.url(), link.title))
        w(u'</p>')
        w(u'</div>')
        # Browse
        w(u'<div class="row">')
        rql = 'Any X WHERE X is IN (QueryDataSet, File)'
        self._build_panel(self._cw._('Dataset'), rql)
        rql = 'Any X WHERE X is Alignment'
        self._build_panel(self._cw._('Alignment'), rql)
        rql = 'Any X WHERE X is AlignmentResult'
        self._build_panel(self._cw._('AlignmentResult'), rql)
        w(u'</div>')


### FACETS
class DatasetTypeFacet(facetbase.AttributeFacet):
    __regid__ = 'dataset-type-facet'
    __select__ = facetbase.AttributeFacet.__select__ & is_instance('QueryDataSet')
    rtype = 'datatype'


def registration_callback(vreg):
    from cubicweb.web.views.bookmark import BookmarksBox
    from cubicweb.web.views.idownloadable import IDownloadablePrimaryView
    vreg.unregister(IDownloadablePrimaryView)
    vreg.unregister(BookmarksBox)
    vreg.unregister(IndexView)
    vreg.register_all(globals().values(), __name__, ())
