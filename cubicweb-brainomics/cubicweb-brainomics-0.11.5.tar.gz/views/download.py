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

import os
import os.path as osp
import tempfile
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED

from cubicweb.predicates import is_instance
from cubicweb.view import EntityView


CSV_DOWNLOADABLE = ('Subject', 'Scan', 'ScoreDefinition', 'QuestionnaireRun',
                    'Answer', 'GenomicMeasure', 'Snp', 'GenericTestRun')
XCEDE_DOWNLOADABLE = ('Subject', 'Scan', 'GenomicMeasure', 'QuestionnaireRun', 'Questionnaire')
JSON_DOWNLOADABLE = ('Subject',)
ZIP_DOWNLOADABLE = ('Scan', 'GenomicMeasure')
ALL_DOWNLOADABLE = set(CSV_DOWNLOADABLE + XCEDE_DOWNLOADABLE + ZIP_DOWNLOADABLE)


###############################################################################
### ZIP VIEWS #################################################################
###############################################################################
class DataZipView(EntityView):
    """Abstract base class for the zip view"""
    __regid__ = 'data-zip'
    __select__ = EntityView.__select__ & is_instance(*ZIP_DOWNLOADABLE)
    templatable = False
    binary = True
    archive_name = 'brainomics_data.zip'

    def _zipfiles(self, filepaths):
        """generates a zip archive from `filepaths`

        :param filepaths: is a set containing tuples with relative file paths
                          as they appear in the archive, and CubicWeb file
                          objects, whose content is put in the archive.

        :return: a couple fileobj, filepath where `fileobj` is a standard python
                 open file objet on the generated archive, and `filepath` is an
                 absolute file path to this archive on the filesystem
        """
        fd, archive_filepath = tempfile.mkstemp()
        try:
            noext_archivename = osp.splitext(self.archive_name)[0]
            with closing(ZipFile(archive_filepath, "w", ZIP_DEFLATED, True)) as zip:
                for filename, gmes_type, subjs, _fileobj in filepaths:
                    for subj in subjs:
                        zip.writestr('%s/%s/%s/%s' % (noext_archivename, gmes_type,
                                                      subj, filename),
                                     _fileobj.read())
            fileobj = os.fdopen(fd)
            fileobj.seek(0)
            return fileobj, archive_filepath
        except:
            os.close(fd)
            os.unlink(archive_filepath)
            raise

    def set_request_content_type(self):
        self._cw.set_content_type('application/zip', filename=self.archive_name)

    def make_entity_labels(self, entity, prefix):
        return ('{0}_{1}'.format(prefix, entity.concerns[0].identifier),)

    def call(self):
        if not self.cw_rset:
            return
        filepaths = set()
        prefix = self._cw._('Subject')
        for entity in self.cw_rset.entities():
            subj = self.make_entity_labels(entity, prefix)
            for _file in entity.results_files:
                if _file.__regid__ == 'FileSet':
                    for _f in _file.file_entries:
                        filepaths.add((_file.dc_title(), entity.dc_title(), subj, _f))
                else:
                        filepaths.add((_file.dc_title(), entity.dc_title(), subj, _file))
        fileobj, archive_filepath = self._zipfiles(list(filepaths))
        try:
            self.w(fileobj.read())
        finally:
            fileobj.close()
            os.unlink(archive_filepath)
