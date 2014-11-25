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

"""cubicweb-suivimp views/forms/actions/components for web ui"""
from logilab.mtconverter import xml_escape
from logilab.common.decorators import monkeypatch

from cubicweb.schema import META_RTYPES, VIRTUAL_RTYPES
from cubicweb.selectors import is_instance
from cubicweb.web.views.primary import PrimaryView

from cubes.brainomics.entities import MEASURES

from cubicweb import NoSelectableObject


###############################################################################
### BRAINOMICS PRIMARY VIEW ###################################################
###############################################################################
class BrainomicsPrimaryView(PrimaryView):
    """ Redefine primary view for html customization """
    hide_undefined_value = False
    hide_empty_string_value = False

    def filter_attributes(self, entity, rschema):
        val_attr = getattr(entity, rschema.type, None)
        if self.hide_undefined_value and val_attr is None:
            return True
        if self.hide_empty_string_value and val_attr == u'':
            return True
        return False

    def filter_relations(self, entity, rschema, role):
        if self.hide_undefined_value and not entity.related(rschema.type, role=role):
            return True
        return False

    def render_entity_attributes(self, entity):
        """Renders all attributes and relations in the 'attributes' section.
        """
        display_attributes = []
        for rschema, _, role, dispctrl in self._section_def(entity, 'attributes'):
            vid = dispctrl.get('vid', 'reledit')
            if rschema.final or vid == 'reledit' or dispctrl.get('rtypevid'):
                if ((rschema.final and self.filter_attributes(entity, rschema)) or
                    (not rschema.final and self.filter_relations(
                        entity, rschema, role=role))):
                    continue
                value = entity.view(vid, rtype=rschema.type, role=role,
                                    initargs={'dispctrl': dispctrl})
            else:
                rset = self._relation_rset(entity, rschema, role, dispctrl)
                if rset:
                    value = self._cw.view(vid, rset)
                else:
                    value = None
            # pylint: disable=E1101
            label = self._rel_label(entity, rschema, role, dispctrl)
            if value is not None and value != '':
                display_attributes.append((dispctrl.get('order', 9999), label, value))
        # BRAINOMICS MODIFICATIONS - Add specific display rset
        for order, label, value in self.iterate_display_rset(entity, 'attributes'):
            display_attributes.append((order, label, value))
        if display_attributes:
            self.w(u'<dl class="dl-horizontal">')
            for order, label, value in sorted(display_attributes, key=lambda x: x[0]):
                self.render_attribute(label, value)
            self.w(u'</dl>')

    def iterate_display_rset(self, entity, section):
        """ Iterate over the display rset from uicfg """
        # Add specific uicfg rset views
        eschema = entity.e_schema
        if section == 'attributes':
            rsetdefs = self.display_ctrl._attrrsetdefs.get(eschema, [])
        elif section == 'relations':
            rsetdefs = self.display_ctrl._relrsetdefs.get(eschema, [])
        else:
            self.warning('Bad section %s for uicfg display rsets' % section)
            return
        for dispctrl in rsetdefs:
            label = dispctrl.get('label')
            if label:
                label = self._cw._(label)
            else:
                label = u''
            # Get order
            order = dispctrl['order'] if 'order' in dispctrl else 9999
            # Get value
            if 'rql' in dispctrl:
                rset = self._cw.execute(dispctrl['rql'] + ', X eid %(e)s', {'e': entity.eid})
                if rset:
                    value = self._cw.view(dispctrl['vid'], rset=rset)
                    if value:
                        yield order, label, value
            elif 'callback' in dispctrl:
                value = dispctrl.get('callback')(entity)
                if value:
                    yield order, label, value

    def render_entity_relations(self, entity):
        """Renders all relations in the 'relations' section."""
        defaultlimit = self._cw.property_value('navigation.related-limit')
        display_relations = []
        for rschema, tschemas, role, dispctrl in self._section_def(entity, 'relations'):
            if rschema.final or dispctrl.get('rtypevid'):
                vid = dispctrl.get('vid', 'reledit')
                try:
                    rview = self._cw.vreg['views'].select(
                        vid, self._cw, rset=entity.cw_rset, row=entity.cw_row,
                        col=entity.cw_col, dispctrl=dispctrl,
                        rtype=rschema, role=role)
                except NoSelectableObject:
                    continue
                value = rview.render(row=entity.cw_row, col=entity.cw_col,
                                     rtype=rschema.type, role=role)
            else:
                vid = dispctrl.get('vid', 'autolimited')
                limit = defaultlimit if vid == 'autolimited' else None
                rset = self._relation_rset(entity, rschema, role, dispctrl, limit=limit)
                if not rset:
                    continue
                if hasattr(self, '_render_relation'):
                    # pylint: disable=E1101
                    self._render_relation(dispctrl, rset, 'autolimited')
                    warn('[3.9] _render_relation prototype has changed and has '
                         'been renamed to render_relation, please update %s'
                         % self.__class__, DeprecationWarning)
                    continue
                try:
                    rview = self._cw.vreg['views'].select(
                        vid, self._cw, rset=rset, dispctrl=dispctrl)
                except NoSelectableObject:
                    continue
                value = rview.render()
            label = self._rel_label(entity, rschema, role, dispctrl)
            display_relations.append((dispctrl.get('order', 9999), label, value))
        # BRAINOMICS MODIFICATIONS - Add specific display rset
        for order, label, value in self.iterate_display_rset(entity, 'relations'):
            display_relations.append((order, label, value))
        if display_relations:
            for order, label, value in sorted(display_relations, key=lambda x: x[0]):
                self.render_relation(label, value)

    def render_attribute(self, label, value):
        self.w(u'<dt>%(label)s</dt><dd>%(value)s</dd>'
               % {'label': xml_escape(self._cw._(label)),
                  'value': value})

    def render_relation(self, label, value):
        self.w(u'<div class="col-md-12">')
        if label:
            self.w(u'<h4>%s</h4>' % label)
        self.w(value)
        self.w(u'</div>')

    def render_entity(self, entity=None):
        entity = entity if entity else self.cw_rset.get_entity(0,0)
        w = self.w
        # Toolbar
        boxes = list(self._cw.vreg['ctxcomponents'].poss_visible_objects(
            self._cw, rset=self.cw_rset, context='nav-toolbar'))
        if boxes:
            w(u'<div class="row navtoolbar">')
            for box in boxes:
                box.render(w=w)
            w(u'</div>')
        # define rsection for similar behavior than CW's primary view
        uicfg_reg = self._cw.vreg['uicfg']
        if self.rsection is None:
            self.rsection = uicfg_reg.select('primaryview_section',
                                             self._cw, entity=entity)
        if self.display_ctrl is None:
            self.display_ctrl = uicfg_reg.select('primaryview_display_ctrl',
                                                 self._cw, entity=entity)
        # BRAINOMICS MODIFICATIONS - Customize html
        w(u'<div class="tab-content">')
        w(u'<div class="tab-pane active" id="entity-mainview">')
        # Attributes
        w(u'<div class="well">')
        w(u'<h2>%s</h2>' % xml_escape(entity.dc_title()))
        self.render_entity_attributes(entity)
        w(u'</div>')
        # Relations
        w(u'<div class="row">')
        self.render_entity_relations(entity)
        w(u'</div>')
        w(u'</div>')
        # BRAINOMICS MODIFICATIONS - Add tabs
        if 'ctx-entity-tabs' in self._cw.vreg:
            tabs = self._cw.vreg['ctx-entity-tabs'].possible_objects(self._cw, rset=self.cw_rset)
            for tab in tabs:
                tab.render(self.w)
        w(u'</div>')


###############################################################################
### REGISTRATION CALLBACK #####################################################
###############################################################################
def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (BrainomicsPrimaryView,))
    vreg.register_and_replace(BrainomicsPrimaryView, PrimaryView)
