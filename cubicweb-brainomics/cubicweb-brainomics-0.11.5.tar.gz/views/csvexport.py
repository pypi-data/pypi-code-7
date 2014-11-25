# -*- coding: utf-8 -*-
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2014 CEA (Saclay, FRANCE), all rights reserved.
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

from cubicweb.web.views.csvexport import CSVRsetView
from cubicweb.predicates import is_instance, one_line_rset


class GenomicMeasureCSVView(CSVRsetView):
    """CSV view for GenomicMeasure"""
    __select__ = (CSVRsetView.__select__ & is_instance('GenomicMeasure')
                  & ~one_line_rset())

    def call(self):
        req = self._cw
        rows = [('"subject identifier"', '"subject admission number"',
                 '"study"', '"type"', '"results_files"')]
        for entity in self.cw_rset.entities():
            study = entity.related_study[0]
            subject = entity.concerns[0]
            admissions = [a for a in subject.reverse_admission_of
                          if a.admission_in[0].eid == study.eid]
            subj_adm_no = (admissions[0].subject_admission_number
                           if admissions else self._cw._('No admission number'))
            rows.append([subject.identifier,
                         subj_adm_no,
                         study.name,
                         entity.type,
                         '; '.join(f.data_name for f in entity.results_files)])
        writer = self.csvwriter()
        writer.writerows(rows)
