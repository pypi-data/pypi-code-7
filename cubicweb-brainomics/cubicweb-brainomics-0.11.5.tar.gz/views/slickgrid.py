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
import json

from cubicweb.utils import make_uid

from cubicweb.web.views import tableview as cw_tableview


"""
This module provides SlickGrid table layout and a SlickgridMixin that
can be used with a TableView to have a SlickGrid representation of the data.

It also provides two implementations of this Mixin:

 * SlickGridRsetTableView

 * SlickGridEntityTableView


These SlickGrid views may be used with:

 * a grid_options attribute (e.g. fro navigation);

 * a default_column_options (e.g. sortable, width, ...);

 * a slickgrid_columns_options that allows to define specific
   options for a given column. The name should be the name
   of a column renderer;

 * a default_formatter attribute;

For each column renderer, without further specifications, a default
column option is built
"""


###############################################################################
### TABLE_SLICKGRID VIEW ######################################################
###############################################################################

class SlickGridTableLayout(cw_tableview.TableLayout):
    __regid__ = 'slickgrid-layout'
    display_filter = 'top'
    hide_filter = False

    def _add_resources(self):
        """ Add the resources (CSS, JS) for slickgrid """
        req = self._cw
        req.add_css('SlickGrid/slick.grid.css')
        req.add_css('cubes.brainomics.slickgrid.css')
        req.add_js('jquery.event.drag-2.2.js')
        req.add_js('SlickGrid/slick.dataview.js')
        req.add_js('SlickGrid/slick.core.js')
        req.add_js('SlickGrid/slick.grid.js')
        req.add_js('SlickGrid/slick.formatters.js')
        req.add_js('cubes.brainomics.slickgrid.js')

    def create_container(self, **options):
        return (u'<div class="slickgrid" id="%(divid)s" '
                u'style="width: %(width)s; height: %(height)s;">'
                u'</div>') % options


    def render_table(self, w, actions, paginate, **kwargs):
        """ Render the slickgrid object """
        self._add_resources()
        self.data = []
        view = self.view
        container_options = view.container_options
        divid = view.domid
        container_options['divid'] = divid
        columns = self.build_grid_column_options()
        data = json.dumps(self.init_data(view, columns))
        grid_options = json.dumps(view.grid_options)
        self._cw.add_onload('cwSlickGrid("#%s", %s, %s, %s)'
                       % (divid,  data,
                          json.dumps(columns),
                          grid_options))
        if actions and self.display_actions == 'top':
            self.render_actions(w, actions)
        w(self.create_container(**container_options))
        if actions and self.display_actions == 'bottom':
            self.render_actions(w, actions)

    def init_data(self, view, columns):
        _columns = set(data['field'] for data in columns)
        colrenderers = view.build_column_renderers()
        rows = []
        for rownum in xrange(self.view.table_size):
            _row = {'id': rownum}
            for colnum, renderer in enumerate(colrenderers):
                stream = []
                w = stream.append
                renderer.render_cell(w, rownum)
                _row[renderer.colid] = stream[-1]
            rows.append(_row)
        return rows

    def build_grid_column_options(self):
        _ = self._cw._
        existing_columns = dict([(c['name'], c)
                                 for c in self.view.slickgrid_columns_options])
        columns = []
        for idx, renderer in enumerate(self.view.build_column_renderers()):
            column_option = existing_columns.get(renderer.colid,
                                                 {'name': renderer.colid})
            columns.append(self.view.build_column_option(idx, column_option))
        return columns


class SlickGridMixIn(object):
    layout_id = 'slickgrid-layout'
    paginable = False
    # slickgrid options
    grid_options = {'enableCellNavigation':True,}
    # columns slickgrid related options
    default_column_options = {'sortable':True}
    # Define in concrete views
    slickgrid_columns_options = ()
    default_formatter = 'HTML'

    def entity(self, rownum):
        """Return the table's main entity"""
        return self.cw_rset.get_entity(rownum, self.cw_col or 0)

    @property
    def container_options(self):
        return {'width':'100%%',
                'height':'400px'}

    def build_column_option(self, idx, column_option):
        column = column_option.copy()
        column['formatter'] = self.default_formatter
        name = _(column_option['name'])
        column['name'] = self._cw._(name)
        if 'id' not in column_option:
            column['id'] = '_c%i' % idx
        if 'field' not in column_option:
            column['field'] = name
        column.update(self.default_column_options)
        return column

    def build_grid_column_options(self):
        _ = self._cw._
        columns = []
        for idx, column_option in enumerate(self.slickgrid_columns_options):
            columns.append(self.build_column_option(idx, column_option))
        return columns


class  SlickGridRsetTableView(SlickGridMixIn, cw_tableview.RsetTableView):
    __regid__ = 'slickgrid-table'


class  SlickGridEntityTableView(SlickGridMixIn, cw_tableview.EntityTableView):
    __abstract__ = True
