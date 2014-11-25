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

from cubicweb.web.action import Action
from cubicweb.predicates import (is_instance, nonempty_rset, anonymous_user,
                                 one_line_rset, match_user_groups, relation_possible)
from cubicweb.web.views.actions import (CopyAction, ModifyAction, DeleteAction,
                                        ManagePermissionsAction, AddRelatedActions)

from cubes.brainomics.views.download import (CSV_DOWNLOADABLE, XCEDE_DOWNLOADABLE,
                                             ZIP_DOWNLOADABLE, JSON_DOWNLOADABLE)


###############################################################################
### ADMIN ACTIONS #############################################################
###############################################################################
class BrainomicsAbstractAdminAction(Action):
    __abstract__ = True
    __select__ = Action.__select__ & nonempty_rset() & match_user_groups('users', 'managers')
    category = 'action-admin'
    icon = 'question-sign'
    title = None    # action title, i18nable


class BrainomicsWikiAdminAction(BrainomicsAbstractAdminAction):
    __regid__ = 'ctx-admin-link-wiki'
    __select__ = BrainomicsAbstractAdminAction.__select__ & relation_possible('wiki')
    title = _('Update wiki')

    def url(self):
        entity = self.cw_rset.get_entity(0, 0)
        card = entity.wiki
        kwargs = {'__redirectpath': entity.rest_path()}
        if not card:
            start_path = 'add/Card'
            kwargs['__linkto'] = 'wiki:%s:object' % entity.eid
        else:
            start_path = card[0].rest_path()
            kwargs['vid'] = 'edition'
        return self._cw.build_url(start_path, **kwargs)


class BrainomicsCommentAdminAction(BrainomicsAbstractAdminAction):
    __regid__ = 'ctx-admin-link-comment'
    __select__ = BrainomicsAbstractAdminAction.__select__ & relation_possible('comments', role='object')
    title = _('Add comment')

    def url(self):
        entity = self.cw_rset.get_entity(0, 0)
        return self._cw.build_url('add/Comment', __linkto='comments:%s:subject' % entity.eid,
                                  __redirectpath=entity.rest_path())

# Add icon for cubicweb admin action
ModifyAction.icon = 'edit'
DeleteAction.icon = 'remove'
ManagePermissionsAction.icon = 'eye-open'


###############################################################################
### DOWNLOAD ACTIONS ##########################################################
###############################################################################
class BrainomicsAbstractDownloadAction(Action):
    __abstract__ = True
    __select__ = Action.__select__ & nonempty_rset() & ~one_line_rset()
    category = 'download-links'


class ScanZipFileBox(BrainomicsAbstractDownloadAction):
    __regid__ = 'scan_zipfile'
    __select__ = BrainomicsAbstractDownloadAction.__select__  & is_instance(*ZIP_DOWNLOADABLE)
    title = _('Download Zip')
    download_vid = 'data-zip'


class CsvFileBox(BrainomicsAbstractDownloadAction):
    __regid__ = 'csvexport'
    __select__ = BrainomicsAbstractDownloadAction.__select__  & is_instance(*CSV_DOWNLOADABLE)
    title = _('Download CSV')
    download_vid = 'csvexport'


class XcedeBox(BrainomicsAbstractDownloadAction):
    __regid__ = 'xcede_file'
    __select__ = BrainomicsAbstractDownloadAction.__select__  & is_instance(*XCEDE_DOWNLOADABLE)
    title = _('Download Xcede')
    download_vid = 'xcede'


class JsonBox(BrainomicsAbstractDownloadAction):
    __regid__ = 'json_file'
    __select__ = BrainomicsAbstractDownloadAction.__select__  & is_instance(*JSON_DOWNLOADABLE)
    title = _('Download Json')
    download_vid = 'ejsonexport'



###############################################################################
### REGISTRATION CALLBACK #####################################################
###############################################################################
def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, ())
    # Desactivate some actions for now
    vreg.unregister(CopyAction)
    vreg.unregister(AddRelatedActions)
