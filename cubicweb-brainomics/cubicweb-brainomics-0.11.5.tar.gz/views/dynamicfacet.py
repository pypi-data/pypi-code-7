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
from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape
import warnings

from cubicweb import ObjectNotFound
from cubicweb.predicates import is_instance, nonempty_rset
from cubicweb.utils import make_uid
from cubicweb.selectors import is_instance
from cubicweb.web.views.ajaxcontroller import ajaxfunc
from cubicweb.appobject import AppObject
from cubicweb.view import View
from cubicweb.web import component, facet as facetbase
from cubicweb.web.facet import FilterRQLBuilder
from cubicweb.web.views import facets

try:
    from cubicweb.web.facet import AbstractRangeRQLPathFacet
    warnings.warn('AbstractRangeRQLPathFacet are now available. '
                  'The file cubes.brainomics.views.rqlpathfacets should be removed')
except ImportError:
    from cubes.brainomics.views.rqlpathfacets import AbstractRangeRQLPathFacet
    warnings.warn('AbstractRangeRQLPathFacet are backport from CW 3.19')


@monkeypatch(facetbase.FilterRQLBuilder)
def build_rql(self):
    form = self._cw.form
    facetids = form['facets']
    # start brainomincs customization
    facetids = facetids.split(',') if isinstance(facetids, basestring) else facetids
    # end brainomincs customization
    # XXX Union unsupported yet
    select = self._cw.vreg.parse(self._cw, form['baserql']).children[0]
    filtered_variable = facetbase.get_filtered_variable(select, form.get('mainvar'))
    toupdate = []
    for facetid in facetids:
        facet = facetbase.get_facet(self._cw, facetid, select, filtered_variable)
        facet.add_rql_restrictions()
        if facet.needs_update:
            toupdate.append(facetid)
    return  select.as_string(), toupdate


class DynamicFacetView(View):
    __regid__ = 'dynamic-facet'

    def call(self):
        vocab = self._cw.form['vocabulary']
        if not vocab:
            return
        rql = self._cw.form['rql']
        vocab = (vocab,) if isinstance(vocab, basestring) else vocab
        facetid = self._cw.form['dynamic-facet-id']
        select = self._cw.vreg.parse(self._cw, rql).children[0]
        rset = self._cw.execute(rql)
        filtered_variable = facetbase.get_filtered_variable(select, None)
        facetbase.prepare_select(select, filtered_variable)
        builder = self._cw.vreg['dynamic-facet-builder'].select_or_none(facetid, self._cw)
        if builder:
            for voc in vocab:
                try:
                    _facet = facetbase.get_facet(self._cw, facetid+voc, select, filtered_variable)
                except ObjectNotFound:
                    _facet = builder.build_facet(voc, rset, select, filtered_variable)
                wdg = _facet.get_widget()
                if wdg:
                    wdg.w = self.w
                    wdg._render()
                    self.w(u'<input type="hidden" name="facets" value="%s" />' %
                           xml_escape(_facet.__regid__))
                else:
                    self.warning('DynamicFacetView : no widget for facet "%s"' % _facet)




class FloatFacetRangeWidget(facetbase.FacetRangeWidget):
    onload = u'''
    var _formatter = %(formatter)s;
    jQuery("#%(sliderid)s").slider({
        range: true,
        min: %(minvalue)s,
        max: %(maxvalue)s,
        step: 0.01,
        values: [%(minvalue)s, %(maxvalue)s],
        stop: function(event, ui) { // submit when the user stops sliding
           var form = $('#%(sliderid)s').closest('form');
           buildRQL.apply(null, cw.evalJSON(form.attr('cubicweb:facetargs')));
        },
        slide: function(event, ui) {
            jQuery('#%(sliderid)s_inf').html(_formatter(ui.values[0]));
            jQuery('#%(sliderid)s_sup').html(_formatter(ui.values[1]));
            jQuery('input[name="%(facetname)s_inf"]').val(ui.values[0]);
            jQuery('input[name="%(facetname)s_sup"]').val(ui.values[1]);
        }
   });
   // use JS formatter to format value on page load
   jQuery('#%(sliderid)s_inf').html(_formatter(jQuery('input[name="%(facetname)s_inf"]').val()));
   jQuery('#%(sliderid)s_sup').html(_formatter(jQuery('input[name="%(facetname)s_sup"]').val()));
'''

    #'# make emacs happier
class DynamicTextInputRangeFacet(facetbase.RangeFacet):
    __abstract__ = True
    wdgclass = FloatFacetRangeWidget
    needs_update = True


class AbstractDynamicRangeFacetBuilder(AppObject):
    __registry__ = 'dynamic-facet-builder'
    __abstract__ = True
    filter_variable = None

    def get_title(self, vocid):
        raise NotImplementedError

    def get_path(self, vocid):
        raise NotImplementedError

    def build_facet(self, vocid, rset, select, filtered_variable):
        class DynamicFacet(AbstractRangeRQLPathFacet, DynamicTextInputRangeFacet):
            __regid__ = self.__regid__ + vocid
            path = self.get_path(vocid)
            filter_variable = self.filter_variable
            title = self.get_title(vocid)
            dynamic_facet = True

        # register the newly created class in facets
        vreg = self._cw.vreg['facets']
        vreg.register(DynamicFacet)
        # register cw_property_defs
        DynamicFacet.__registered__(vreg)

        # Facet rendering
        _facet = DynamicFacet(self._cw, select, filtered_variable)
        _facet.cw_rset = rset
        return _facet


class AbstractDynamicFacetBox(component.Component):
    __registry__ = 'dynamic-facet'
    __abstract__ = True
    title = None
    __select__ = component.Component.__select__  & nonempty_rset()

    def get_vocabulary(self):
        raise NotImplementedError

    def render(self, w, **kwargs):
        w(u'<h5>%s</h5>' % self._cw._(self.title))
        w(u'<select id="%s" multiple>' % self.__regid__)
        for eid, name in self.get_vocabulary():
            w(u'<option name=%s value=%s> %s </option>' % (name, eid, name))
        w(u'</select>')
        w(u'''<button onclick="cw.cubes.brainomics.addDynamicFacet('%s');return false;"
              class="btn btn-default">%s</button>''' % (self.__regid__, self._cw._('Filter')))

