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

"""cubicweb-vcwiki entity's classes"""

import os.path as osp

import mimetypes
mimetypes.add_type('text/rest', '.rst')

from logilab.common.decorators import cached, cachedproperty

from cubicweb.entities import AnyEntity
from cubicweb.entities.adapters import IFTIndexableAdapter
from cubicweb.predicates import is_instance, match_form_params
from cubicweb.web.views.ibreadcrumbs import IBreadCrumbsAdapter

from cubes.vcwiki import is_vfile_of_wiki


def split_path(path):
    """ Return a tuple (file directory, file name) deduced from the `path`
    parameter. This method uses '/' as a separator between file directory
    and path.
    """
    filedir, sep, name = path.rpartition('/')
    return filedir, name


class VCWiki(AnyEntity):
    __regid__ = 'VCWiki'

    @property
    def repository(self):
        """ Short accessor to the wiki's repository. """
        return self.content_repo[0]

    @property
    def urlpath(self):
        """ Path part of the wiki's URL. """
        return 'wiki/%s/' % self._cw.url_quote(self.name)

    @property
    def url(self):
        """ URL of the current wiki. """
        return self._cw.build_url(self.urlpath)

    def page_urlpath(self, path):
        """ Path part of a wiki page's URL. """
        return self.urlpath + self._cw.url_quote(path, safe='/')

    def page_url(self, path, **kwargs):
        """ Helper to build the URL of the wiki page's that has `path` path.
        Use additional keyword args to specify other URL parameters, like "vid".
        """
        return self._cw.build_url(self.page_urlpath(path), **kwargs)

    def vcpage_path(self, wikipath):
        """ Transform `wikipath`, a url path part of the web wiki, into the path
        of the corresponding wiki page in the mercurial repository, adding the 
        vcwiki's content file extension.
        """
        wikipath = wikipath or 'index' # handle root url path
        return wikipath + '.' + self.content_file_extension

    @cached
    def current_changeset(self):
        rset = self.repository.cw_adapt_to('VCSRepo').log_rset(revrange='tip')
        if not rset:
            return '0' * 12
        return next(rset.entities()).changeset

    def content(self, path, revision=None, allow_deleted=False):
        """ Return the content of the file with given path if it exists in the
        given revision (or latest one if None) of current wiki's repository.

        If the `allow_deleted` parameter is True, a DeletedVersionContent can be
        returned, if any. Otherwise, deleted content will lead to a None value.

        If nothing was found, return None.
        """
        if revision is None:
            revision = self.current_changeset()
        try:
            return self.repository.cw_adapt_to('VCSRepo').cat(rev=revision, path=path)
        except Exception:
            if allow_deleted and self.repository.cw_adapt_to('VCSRepo').file_deleted(path):
                return False
            return None

    def __contains__(self, path):
        return path in self.repository.cw_adapt_to('VCSRepo')

    def display_name(self, path):
        """Return a displayable name for a page -normally part of the
        wiki's content-, build by stripping the trailing vcwiki's extension,
        if present."""
        name = osp.basename(path)
        ext = '.' + self.content_file_extension
        if name.endswith(ext):
            name = name[:-len(ext)]
        return name

    @cachedproperty
    def content_mimetype(self):
        return mimetypes.types_map.get('.' + self.content_file_extension,
                                       'text/plain')


class VCWikiBreadcrumbs(IBreadCrumbsAdapter):
    """ Breadcrumbs adapter for VCWiki entities to expose the directory
    structure of the wiki.
    """
    __select__ = (IBreadCrumbsAdapter.__select__ & is_instance('VCWiki') &
                  match_form_params('wikipath'))

    @property
    def vcpath(self):
        return self.entity.vcpage_path(self._cw.form['wikipath'])

    def breadcrumbs(self, view=None, recurs=None):
        """Hierarchy of wiki pages following its repository's directory-like
        structure. Return a link to the index page of the parent directories.
        """
        path = []
        vcwiki = self.entity
        wikipath = self._cw.form['wikipath']
        if wikipath and self.vcpath in vcwiki: # skip root path and 404
            dirs = self.vcpath.split('/')[:-1]
            path.append(wikipath.split('/')[-1])
            while dirs:
                dirpath = u'/'.join(dirs)
                dirname = dirs.pop()
                vcontent = vcwiki.content(vcwiki.vcpage_path(dirpath))
                if vcontent is not None:
                    path.append((vcwiki.page_url(dirpath), dirname))
                else:
                    path.append(dirname)
        path.append((vcwiki.url, vcwiki.name))
        path.reverse()
        return path
