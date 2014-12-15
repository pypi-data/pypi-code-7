from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import (
    newSecurityManager, setSecurityManager
)
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from contextlib import contextmanager
from plone import api


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """
    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


@contextmanager
def run_as(role):
    """ Execute code under special role priviledges.

    For example:

    with run_as('Manager'):
        do_dangerous_things()

    Please note that this is dangerous and should only be used in a very
    limited and well understood fashion. Try to do as little as possible.

    Better yet, find a way around this.
    """

    sm = getSecurityManager()
    portal = api.portal.get()

    try:
        try:
            # Clone the current user and assign a new role.
            # Note that the username (getId()) is left in exception
            # tracebacks in the error_log,
            # so it is an important thing to store.
            tmp_user = UnrestrictedUser(
                sm.getUser().getId(), '', [role], ''
            )

            # Wrap the user in the acquisition context of the portal
            tmp_user = tmp_user.__of__(portal.acl_users)
            newSecurityManager(None, tmp_user)

            yield

        except:
            # If special exception handlers are needed, run them here
            raise
    finally:
        # Restore the old security manager
        setSecurityManager(sm)
