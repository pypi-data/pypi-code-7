import os

import hglib

from cubicweb import Binary
from cubicweb.server import Service

from cubes.vcsfile import bridge


class RevisionDiffService(Service):
    """ Return the diff between two revisions.
    """

    __regid__ = 'vcwiki.export-rev-diff'

    def call(self, repo_eid, path, rev1, rev2):
        repo = self._cw.entity_from_eid(repo_eid)
        adapter = repo.cw_adapt_to('VCSRepo')
        filepath = os.path.join(adapter.path, path)
        try:
            with adapter.hgrepo() as hgrepo:
                out_diff = hgrepo.diff(files=[filepath.encode(repo.encoding)],
                                       revs=[rev1, rev2], git=True, unified=5)
            return out_diff
        except hglib.error.ServerError:
            return None
