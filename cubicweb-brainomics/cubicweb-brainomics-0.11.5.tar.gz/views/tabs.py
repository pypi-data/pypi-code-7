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

from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance, nonempty_rset, relation_possible
from cubicweb.web import component


###############################################################################
### TABBLABLE SELECTION COMPONENT #############################################
###############################################################################
class BrainomicsTabblableSelectionComponent(component.CtxComponent):
    """ Component of selection of the different tabs
    """
    __select__ = component.CtxComponent.__select__ & nonempty_rset()
    context = 'nav-toolbar'
    __regid__ = 'tabblable-select-ctx'

    def render(self, w, **kwargs):
        if 'ctx-entity-tabs' in self._cw.vreg:
            tabs = list(self._cw.vreg['ctx-entity-tabs'].possible_objects(self._cw,
                                                                          rset=self.cw_rset))
        else:
            tabs = []
        if tabs:
            w(u'<ul class="nav nav-pills" id="entity-tab">')
            # Main info
            w(u'<li class="active"><a href="#entity-mainview" data-toggle="pill" '
              'class="bnt btn-warning">%s</a></li>' % xml_escape(self._cw._('Main info')))
            # Other tabs
            for tab in tabs:
                w(u'<li><a href="#%s" data-toggle="pill" class="bnt btn-warning">%s</a></li>'
                  % (tab.__regid__, tab.get_title()))
            w(u'</ul>')


class AbstractBrainomicsTabblable(component.EntityCtxComponent):
    """ Component used to display a tab. """
    __abstract__ = True
    __registry__ = 'ctx-entity-tabs'

    def get_title(self):
        return

    def render_content(self, w, **kwargs):
        return

    def render(self, w, **kwargs):
        w(u'<div class="tab-pane" id="%s">' % self.__regid__)
        self.render_content(w)
        w(u'</div>')


###############################################################################
### TABBLABLE COMPONENTS - COMMENT ############################################
###############################################################################
class BrainomicsTabblableComment(AbstractBrainomicsTabblable):
    """ Component used to display a tab with comment. """
    __select__ = AbstractBrainomicsTabblable.__select__ & relation_possible('comments', role='object')
    __regid__ = 'entity-comment-tab'

    def get_title(self):
        return self._cw._('Comments')

    def render_content(self, w, **kwargs):
        entity = self.cw_rset.get_entity(0, 0)
        comp = self._cw.vreg['ctxcomponents'].select_or_none('commentsection',
                                                             self._cw, rset=self.cw_rset,
                                                             entity=entity, __cache=None)
        if comp is not None:
            comp.render(w=w)


###############################################################################
### TABBLABLE COMPONENTS - WIKI ###############################################
###############################################################################
class BrainomicsTabblableWiki(AbstractBrainomicsTabblable):
    """ Component used to display a tab with wiki. """
    __select__ = AbstractBrainomicsTabblable.__select__ & relation_possible('wiki')
    __regid__ = 'entity-wiki-tab'

    def get_title(self):
        return self._cw._('Documentation')

    def render_content(self, w, **kwargs):
        entity = self.cw_rset.get_entity(0, 0)
        card_rset = self._cw.execute('Any X WHERE X is Card, Q wiki X, Q eid %(eid)s',
                                {'eid': entity.eid})
        if card_rset:
            w(self._cw.view('documentation_card', rset=card_rset))
        else:
            w(u'<div>%s</div>' % self._cw._('No documentation available'))


###############################################################################
### TABBLABLE COMPONENTS - TIMELINE ###########################################
###############################################################################
class BrainomicsTabblableTimeline(AbstractBrainomicsTabblable):
    """ Component used to display a tab with a timeline. """
    __select__ = AbstractBrainomicsTabblable.__select__ & is_instance('Subject')
    __regid__ = 'entity-timeline-tab'

    def get_title(self):
        return self._cw._('Timeline')

    def render_content(self, w, **kwargs):
        w(self._cw.view('vtimeline', rset=self.cw_rset))


###############################################################################
### TABBLABLE COMPONENTS - JQPLOT #############################################
###############################################################################
class BrainomicsTabblableJqplotQuestion(AbstractBrainomicsTabblable):
    __select__ = AbstractBrainomicsTabblable.__select__ & is_instance('Question')
    __regid__ = 'entity-jqplot-tab'

    def get_title(self):
        return self._cw._('Plot')

    def get_values_rset(self):
        # XXX Adapter ?
        entity = self.cw_rset.get_entity(0, 0)
        return self._cw.execute('Any V, COUNT(A) GROUPBY V WHERE A is Answer, '
                                'A question Q, Q eid %(e)s, A value V', {'e': entity.eid})

    def render_content(self, w, **kwargs):
        entity = self.cw_rset.get_entity(0, 0)
        rset = self.get_values_rset()
        jsbind = self.add_jsbind(w)
        if rset:
            w(self._cw.view('jqplot-2col', tab_id='pill', rset=rset, jsbind=jsbind,
                            title=xml_escape(entity.dc_title()),
                            displayactions=True, actions=('print',),
                            legend={'show': False}, width='100%'))
        else:
            w(u'<div>%s</div>' % self._cw._('No values available'))

    def get_rql(self):
        entity = self.cw_rset.get_entity(0, 0)
        return 'Any A WHERE A is Answer, A question Q, Q eid %s, A value' % entity.eid

    def add_jsbind(self, w):
        w(u'<div id="jqplot-info"></div>')
        jsbind = """function (ev, seriesIndex, pointIndex, data) {
        var htmlstr = data[0] + ' : ' + data[1] + ' entries';
        var url = '%s?rql=' + '%s ' + data[0];
        var htmlstr = htmlstr + '   <a href="' + url +'">See all</a>';
        $('#jqplot-info').html(htmlstr);
        }""" % (self._cw.base_url(), self.get_rql())
        return jsbind


class BrainomicsTabblableJqplotScoreDef(BrainomicsTabblableJqplotQuestion):
    __select__ = AbstractBrainomicsTabblable.__select__ & is_instance('ScoreDefinition')

    def get_values_rset(self):
        # XXX Adapter ?
        entity = self.cw_rset.get_entity(0, 0)
        if entity.type == 'numerical':
            rset = self._cw.execute('Any V, COUNT(S) GROUPBY V WHERE S value V, '
                                    'S is ScoreValue, S definition D, D eid %(e)s',
                                    {'e': entity.eid})
        else: # Text
            rset = self._cw.execute('Any V, COUNT(S) GROUPBY V WHERE S text V, '
                                    'S is ScoreValue, S definition D, D eid %(e)s',
                                    {'e': entity.eid})
        return rset

    def get_rql(self):
        entity = self.cw_rset.get_entity(0, 0)
        if entity.type == 'numerical':
            return 'Any S WHERE S is ScoreValue, S definition D, D eid %s, S value' % entity.eid
        else: # Text
            return 'Any S WHERE S is ScoreValue, S definition D, D eid %s, S text' % entity.eid

    def add_jsbind(self, w):
        w(u'<div id="jqplot-info"></div>')
        entity = self.cw_rset.get_entity(0, 0)
        if entity.type == 'numerical':
            jsbind = """function (ev, seriesIndex, pointIndex, data) {
            var htmlstr = data[0] + ' : ' + data[1] + ' entries';
            var url = '%s?rql=' + '%s ' + data[0];
            var htmlstr = htmlstr + '   <a href="' + url +'">See all</a>';
            $('#jqplot-info').html(htmlstr);
            }""" % (self._cw.base_url(), self.get_rql())
        else: # Text
            jsbind = """function (ev, seriesIndex, pointIndex, data) {
            var htmlstr = ticks[pointIndex] + ' : ' + data[1] + ' entries';
            var url = '%s?rql=' + '%s "' + ticks[pointIndex] + '"';
            console.log(url)
            var htmlstr = htmlstr + "   <a href='" + url +"'>See all</a>";
            $('#jqplot-info').html(htmlstr);
            }""" % (self._cw.base_url(), self.get_rql())
        return jsbind


###############################################################################
### TABBLABLE COMPONENTS - ASSESSMENTS ########################################
###############################################################################
class BrainomicsTabblableAssessmentView(AbstractBrainomicsTabblable):
    __select__ = AbstractBrainomicsTabblable.__select__ & is_instance('Subject')
    __regid__ = 'subject-assessment-tab'

    def get_title(self):
        return self._cw._('Assessments')

    def render_content(self, w, **kwargs):
        entity = self.cw_rset.get_entity(0, 0)
        rset = self._cw.execute('Any X WHERE S concerned_by X, S eid %(e)s', {'e': entity.eid})
        if rset:
            w(self._cw.view('sameetypelist', rset=rset))


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      (BrainomicsTabblableTimeline,))
    if 'vtimeline' in vreg.config.cubes():
        vreg.register(BrainomicsTabblableTimeline)
