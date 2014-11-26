from warnings import warn
from contextlib import contextmanager
from cubicweb.server.repository import Repository
from cubicweb import UnknownEid


def getrepo(obj):
    """ obj could be either:
    * an appobject carrying a _cw
    * a repo
    """
    if not isinstance(obj, Repository):
        try:
            repo = obj._cw.repo
        except AttributeError:
            repo = obj._cw.vreg.config.repository()
    else:
        repo = obj
    assert repo
    return repo

@contextmanager
def temp_session(obj):
    """ obj is either an appobject or an immediate Repository instance"""
    warn('[worker 3.0.0] temp_session is better replaced with the '
         'repo.internal_cnx context manager',
         DeprecationWarning)
    repo = getrepo(obj)
    cnx = repo.internal_cnx()
    try:
        yield cnx
    finally:
        cnx.close()


def refresh(cnx, entity):
    """Return new entity on the target session

    the new entity is free of any cache"""
    entity = cnx.entity_from_eid(entity.eid)
    entity.cw_clear_all_caches()
    return entity


class UtilsHolder(object):
    """Work around reload issue"""

    def temp_cnx(self):
        """More work around"""
        return getrepo(self).internal_cnx()


    @staticmethod
    def refresh(cnx, entity):
        return refresh(cnx, entity)

    @staticmethod
    def commit_transition(entity, transition, message=None, lenient=False):
        """fire the requested transition for an entity
        this can fail:
        * when a user aborts an operation from the gui
        * if another competing worker grabbed a task first

        the transition is fired in a temporary dedicated connection and commited
        during this function.

        returns a transition object (success) or None (failure)
        """
        with getrepo(entity).internal_cnx() as cnx:
            try:
                entity = refresh(cnx, entity)
            except UnknownEid:
                entity.warning('looks like the entity %s is gone ...', entity.eid)
                return
            adapter = entity.cw_adapt_to('IWorkflowable')
            target_trans = set(tr.name for tr in adapter.possible_transitions())
            if transition not in target_trans:
                # let's log immediately the upcoming pb
                # fire_transition failure will be caught by callers
                msg = '%s in state %s cannot switch to %s (allowed: %s)'
                loggit = entity.error
                if lenient:
                    loggit = entity.warning
                loggit(msg, entity.dc_title(), adapter.state,
                       transition, target_trans)
            tr = adapter.fire_transition(transition, message and unicode(message) or None)
            cnx.commit()
            return tr
