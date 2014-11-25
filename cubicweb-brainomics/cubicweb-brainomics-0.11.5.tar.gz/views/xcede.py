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

from cubicweb.selectors import is_instance
from cubicweb.web.views.xmlrss import XMLView, XMLItemView


###############################################################################
### BASE XCEDE VIEW ###########################################################
###############################################################################
class XcedeView(XMLView):
    """Xcede import"""
    __regid__ = 'xcede'
    title = _('xcede export')
    templatable = False
    content_type = 'text/xml'
    item_vid = 'xcede-item'

    def cell_call(self, row, col):
        self.wview(self.item_vid, self.cw_rset, row=row, col=col)

    def call(self):
        """display a list of entities by calling their <item_vid> view"""
        self.w(u'<?xml version="1.0" encoding="%s"?>\n' % self._cw.encoding)
        self.w(u'<XCEDE xmlns:xcede="http://www.xcede.org/xcede.org/xcede-2" '
               'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n')
        for i in xrange(self.cw_rset.rowcount):
            self.cell_call(i, 0)
        self.w(u'</XCEDE>\n')


###############################################################################
### MEDICALEXP ################################################################
###############################################################################
class SubjectXcedeItemView(XMLItemView):
    __select__ = XMLItemView.__select__ & is_instance('Subject')
    __regid__ = 'xcede-item'
    templatable = False

    def entity_call(self, entity):
        """element as an item for an xml feed"""
        entity.complete()
        self.w(u'<subject ID="%s"/>\n' % entity.identifier)
        # Assessments
        rset = self._cw.execute('Any M WHERE S concerned_by M, M is Assessment, S eid %(e)s',
                                {'e': entity.eid})
        self.wview('xcede-item', rset)
        # Scans, Questionnaires
        # XXX Only use it for now if we have less than 10 subjects - time consuming
        if len(self.cw_rset) < 10:
            for etype in ('Scan', 'QuestionnaireRun', 'GenomicMeasure'):
                rset = self._cw.execute('Any M WHERE M concerns S, S eid %%(e)s, '
                                        'M is %s' % etype, {'e': entity.eid})
                if rset:
                    self.wview('xcede-item', rset)


# XXX AbstractMeasureXcedeItemView ?
# XXX Subjectgroup ?
# XXX link assessment -> studies ?

class AssessmentXcedeItemView(XMLItemView):
    __select__ = XMLItemView.__select__ & is_instance('Assessment')
    __regid__ = 'xcede-item'
    templatable = False

    def entity_call(self, entity):
        """element as an item for an xml feed"""
        entity.complete()
        subject = entity.reverse_concerned_by[0]
        # XXX studyID/visitID -> Assessment
        self.w(u'<visit ID="%(id)s" projectID="%(p)s" subjectID="%(s)s"/>\n'
               % {'id':xml_escape(entity.cwuri),
                  'p': xml_escape(subject.related_studies[0].name),
                  's': xml_escape(subject.identifier)})


class StudyXcedeItemView(XMLItemView):
    __select__ = XMLItemView.__select__ & is_instance('Study')
    __regid__ = 'xcede-item'
    templatable = False

    def entity_call(self, entity):
        """element as an item for an xml feed"""
        entity.complete()
        self.w(u'<project ID="%s">\n' % xml_escape(entity.name))
        self.w(u'<projectInfo>\n')
        self.w(u'<subjectGroupList>\n')
        groups = {}
        rset = self._cw.execute('Any GI, SIS WHERE S related_groups G, S related_studies SI, '
                                'SI eid %(e)s, G identifier GI, S identifier SIS', {'e': entity.eid})
        for gi, si in rset:
            groups.setdefault(gi, []).append(si)
        for gi, sis in groups.iteritems():
            self.w(u'<subjectGroup ID="%s">\n' % gi)
            for si in sis:
                self.w(u'<subjectID>%s</subjectID>\n' % si)
            self.w(u'</subjectGroup>\n')
        self.w(u'</subjectGroupList>\n')
        self.w(u'</projectInfo>\n')
        self.w(u'</project>\n')
        # Add subjects
        # XXX Not used for now, time consuming
        ## rset = self._cw.execute('Any S WHERE S related_studies SI, SI eid %(e)s', {'e': entity.eid})
        ## self.wview('xcede-item', rset)


###############################################################################
### QUESTIONNAIRE #############################################################
###############################################################################
class QuestionnaireXcedeItemView(XMLItemView):
    __select__ = XMLItemView.__select__ & is_instance('Questionnaire')
    __regid__ = 'xcede-item'
    templatable = False

    def entity_call(self, entity):
        """element as an item for an xml feed"""
        entity.complete()
        # XXX studyID/visitID -> Assessment
        self.w(u'<xcede:step ID="%(id)s" name="%(la)s" minOccurences="1" maxOccurences="1" required="true">'
               % {'id':xml_escape(entity.identifier), 'la': xml_escape(entity.name)})
        # Questions/answers
        rset = self._cw.execute('Any Q, QI, QP, QT, QTY, QPA ORDERBY QP ASC '
                                'WHERE QQ is Questionnaire, QQ eid %(e)s, '
                                'Q questionnaire QQ, Q identifier QI, Q position QP, Q text QT, '
                                'Q type QTY, Q possible_answers QPA',
                                {'e': entity.eid})
        self.w(u'<xcede:items>')
        self.wview('xcede-item', rset)
        self.w(u'</xcede:items>')
        self.w(u'</xcede:step>')


class QuestionXcedeItemView(XMLItemView):
    __select__ = XMLItemView.__select__ & is_instance('Question')
    __regid__ = 'xcede-item'
    templatable = False

    def entity_call(self, entity):
        """element as an item for an xml feed"""
        entity.complete()
        self.w(u'<xcede:item ID="%s">\n' % entity.identifier)
        self.w(u'<xcede:itemText><xcede:textLabel location="leadText" value="%s"/></xcede:itemText>\n'
               % entity.text)
        self.w(u'<xcede:itemChoice itemCode="1" itemValue="%s"/>\n' % entity.possible_answers)
        self.w(u'</xcede:item>\n')


class QuestionnaireRunXcedeItemView(XMLItemView):
    __select__ = XMLItemView.__select__ & is_instance('QuestionnaireRun')
    __regid__ = 'xcede-item'
    templatable = False

    def entity_call(self, entity):
        """element as an item for an xml feed"""
        entity.complete()
        assessment = entity.reverse_generates[0] if entity.reverse_generates else None
        questionnaire = entity.instance_of[0]
        # XXX studyID/visitID -> Assessment
        self.w(u'<xcede:data xsi:type="xcede:assessment_t" subjectID="%s">\n'
               % xml_escape(entity.concerns[0].identifier))
        self.w(u'<xcede:name>%s</xcede:name>\n' % xml_escape(questionnaire.name))
        self.w(u'<xcede:dataInstance validated="%s">\n' % entity.valid)
        if questionnaire.note:
            self.w(u'<xcede:assessmentInfo><xcede:description>%s</xcede:description></xcede:assessmentInfo>'
                   % xml_escape(questionnaire.note))
        rset = self._cw.execute('Any AV, QI, QP ORDERBY QP ASC WHERE A is Answer, A question Q, '
                                'Q position QP, Q identifier QI, A value AV, A questionnaire_run QR, QR eid %(e)s',
                                {'e': entity.eid})
        for value, qid, qp in rset:
            self.w(u'<xcede:assessmentItem ID="%s"><xcede:value>%s</xcede:value></xcede:assessmentItem>\n'
                  % (xml_escape(qid), value))
        self.w(u'</xcede:dataInstance>\n')
        self.w(u'</xcede:data>\n')
        # Questionnaire
        # XXX Should be unique in the document
        ## questionnaire.view('xcede-item', w=self.w)


###############################################################################
### NEUROIMAGING ##############################################################
###############################################################################
class ScanXcedeItemView(XMLItemView):
    __select__ = XMLItemView.__select__ & is_instance('Scan')
    __regid__ = 'xcede-item'
    templatable = False

    def entity_call(self, entity):
        """element as an item for an xml feed"""
        entity.complete()
        assessment = entity.reverse_generates[0] if entity.reverse_generates else None
        # XXX studyID/visitID -> Assessment
        self.w(u'<acquisition ID="%(id)s" projectID="%(p)s" subjectID="%(s)s" '
               'visitID="%(a)s" studyID="%(a)s" episodeID="%(la)s"/>\n'
               % {'id': xml_escape(entity.cwuri),
                  'p': xml_escape(entity.related_study[0].name),
                  's': xml_escape(entity.concerns[0].identifier),
                  'a': xml_escape(assessment.cwuri) if assessment else None,
                  'la': xml_escape(entity.label)})
        if entity.has_data:
            entity.has_data[0].view('xcede-item', w=self.w)


class MRIDataXcedeItemView(XMLItemView):
    __select__ = XMLItemView.__select__ & is_instance('MRIData')
    __regid__ = 'xcede-item'
    templatable = False

    def entity_call(self, entity):
        """element as an item for an xml feed"""
        entity.complete()
        scan = entity.reverse_has_data[0]
        self.w(u'<dataResource xsi:type="dimensionedBinaryDataResource_t">\n')
        self.w(u'<uri offset="0" size="262144">%s</uri>\n' % xml_escape(scan.full_filepath))
        ##self.w(u'<elementType>int32</elementType>')
        ##self.w(u'<byteOrder>msbfirst</byteOrder>')
        self.w(u'<elementType>float32</elementType>')
        self.w(u'<compression>%s</compression>' % xml_escape(scan.format))
        if entity.shape_x:
            self.w(u'<dimension label="x">\n')
            self.w(u'<size>%s</size>' % entity.shape_x)
            self.w(u'<spacing>%s</spacing>' % entity.voxel_res_x)
            # XXX harc-coded ?
            self.w(u'<direction>1 0 0</direction>\n')
            self.w(u'<units>mm</units>\n')
            self.w(u'</dimension>\n')
        if entity.shape_y:
            self.w(u'<dimension label="y">\n')
            self.w(u'<size>%s</size>' % entity.shape_y)
            self.w(u'<spacing>%s</spacing>' % entity.voxel_res_y)
            # XXX harc-coded ?
            self.w(u'<direction>0 1 0</direction>\n')
            self.w(u'<units>mm</units>\n')
            self.w(u'</dimension>\n')
        if entity.shape_z:
            self.w(u'<dimension label="y">\n')
            self.w(u'<size>%s</size>' % entity.shape_z)
            self.w(u'<spacing>%s</spacing>' % entity.voxel_res_z)
            # XXX harc-coded ?
            self.w(u'<direction>0 0 1</direction>\n')
            self.w(u'<units>mm</units>\n')
            self.w(u'</dimension>\n')
        self.w(u'</dataResource>\n')


###############################################################################
### GENOMIC ###################################################################
###############################################################################
class GenomicMeasureXcedeItemView(XMLItemView):
    __select__ = XMLItemView.__select__ & is_instance('GenomicMeasure')
    __regid__ = 'xcede-item'
    templatable = False

    def entity_call(self, entity):
        """element as an item for an xml feed"""
        entity.complete()
        assessment = entity.reverse_generates[0] if entity.reverse_generates else None
        # XXX studyID/visitID -> Assessment
        self.w(u'<acquisition ID="%(id)s" projectID="%(p)s" subjectID="%(s)s" '
               'visitID="%(a)s" studyID="%(a)s" episodeID="%(la)s"/>\n'
               % {'id': xml_escape(entity.cwuri),
                  'p': xml_escape(entity.related_study[0].name),
                  's': xml_escape(entity.concerns[0].identifier),
                  'a': xml_escape(assessment.cwuri) if assessment else None,
                  'la': xml_escape(entity.type)})
