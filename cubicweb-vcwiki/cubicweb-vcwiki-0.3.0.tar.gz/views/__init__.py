# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-vcwiki views"""


from logilab.common.decorators import cachedproperty

from cubicweb.predicates import is_instance, match_form_params, objectify_predicate
from cubicweb.view import EntityView


@objectify_predicate
def has_write_perm_on_repo(cls, req, rset=None, entity=None, col=0, **kwargs):
    """Predicate to be complemented by is_instance('VCWiki'), that will return
    1 in the case the given VCWiki has a content repository on which current
    user as the update permission.
    """
    entity = entity or (rset and rset.get_entity(0, col))
    repo = entity.content_repo[0]
    rset = req.user.has_permission('write', contexteid=repo.eid)
    if rset:
        return 1
    return 0

def is_vcwiki_page(vcwiki):
    form = vcwiki._cw.form
    if 'wikipath' in form:
        vcpage_path = vcwiki.vcpage_path(form['wikipath'])
        if vcwiki.content(vcpage_path):
            return 1


class VCWikiView(EntityView):
    __abstract__ = True
    __select__ = (EntityView.__select__
                  & is_instance('VCWiki')
                  & match_form_params('wikipath'))
    consider_rev_parameter = False

    @property
    def vcontent(self):
        """ Return the contents of the current path in current vcwiki. This
        will consider the `rev` url parameter (which must contain a revision
        number) if the attribute `consider_rev_parameter` is set (which is not
        the default).
        """
        form = self._cw.form
        revnum = None
        if self.consider_rev_parameter:
            revnum = form.get('rev')
        vcpage_path = self.vcwiki.vcpage_path(form['wikipath'])
        return self.vcwiki.content(vcpage_path, revision=revnum)

    @property
    def vcpage_path(self):
        form = self._cw.form
        return self.vcwiki.vcpage_path(form['wikipath'])

    @cachedproperty
    def vcwiki(self):
        return self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
