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

from cubicweb.utils import json_dumps, js_dumps, JSString
from cubicweb.predicates import multi_columns_rset

from cubes.jqplot.views import JQPlotSimpleView


################################################################################
### JQPLOT RSET VIEW ###########################################################
################################################################################
class BrainomicsRsetJqplot(JQPlotSimpleView):
    __regid__ = 'jqplot-2col'
    __select__ = multi_columns_rset(2)

    def call(self, rset=None, tab_id=None, jsbind=None, renderer=None, options=None,
             divid=None, legend=None, colors=None,
             width=450, height=300, displayfilter=False, mainvar=None, title=None,
             displayactions=False, actions=None):
        # Refefine the call() function to allow to pass an rset
        if self._cw.ie_browser():
            self._cw.add_js('excanvas.js')
        self._cw.add_js(('jquery.jqplot.js', 'cubes.jqplot.js', 'cubes.jqplot.ext.js'))
        self._cw.add_css('jquery.jqplot.min.css')
        data, ticks = self.get_data(rset)
        if legend is None:
            legend = self.default_legend
        if divid is None:
            divid = u'figure%s' % self._cw.varmaker.next()
        if renderer is None:
            renderer = self.default_renderer
        serie_options = {'renderer': self.renderer(self.renderers, renderer)}
        if options is None:
            options = self.default_options
        serie_options['rendererOptions']= options
        options = {'series': [serie_options],
                   'legend': legend,
                   'title': title,
                   }
        if ticks:
            self._cw.html_headers.add_onload('ticks = %s' % json_dumps(ticks))
            options['axes'] = {'xaxis': {'ticks': JSString('ticks'),
                                         'renderer': JSString('$.jqplot.CategoryAxisRenderer')}}
            self._cw.add_js('plugins/jqplot.categoryAxisRenderer.min.js')
        if colors is not None:
            options['seriesColors'] = colors
        self.set_custom_options(options)
        # Allow an onload on tab/pill show
        js_onload  = self.onload % {'id': divid, 'data': json_dumps([data]),
                                    'options': js_dumps(options)}
        if not tab_id:
            self._cw.html_headers.add_onload(js_onload)
        else:
            self._cw.html_headers.add_onload("""$('a[data-toggle="%s"]').on('shown.bs.tab',
            function (e) {%s})""" % (tab_id, js_onload))
        self.div_holder(divid, width, height)
        if displayfilter and not 'fromformfilter' in self._cw.form:
            self.form_filter(divid, mainvar)
        if displayactions and not 'fromformfilter' in self._cw.form:
            self.display_actions(divid, actions)
        # Add a js bind function
        if jsbind:
            self._cw.html_headers.add_onload("""$('#%s').bind('jqplotDataClick',%s)"""
                                             % (divid, jsbind))

    def get_data(self, rset=None):
        rset = rset or self.cw_rset
        if isinstance(rset[0][0], basestring):
            ticks = list(set([r[0] for r in rset if r[0] is not None and r[1] is not None]))
            data = [[ticks.index(r[0]), r[1]] for r in rset if r[0] is not None and r[1] is not None]
            return [d[1] for d in sorted(data, key=lambda x: x[0])], ticks
        else:
            return [[r[0], r[1]] for r in rset if r[0] is not None and r[1] is not None], None
