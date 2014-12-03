from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.interfaces import IAuthenticationPolicy

from zope.interface import implementer


@implementer(IAuthenticationPolicy)
class DebugAuthenticationPolicy(CallbackAuthenticationPolicy):
    """Debug Authentication Policy

    Set plain authentication details in the Authentication http header:

        Authentication: Debug user_id [principal1] [principal2] [...]
    """
    def __init__(self, callback=None):
        self._callback = callback

    def unauthenticated_userid(self, request):
        """ The userid parsed from the ``Authorization`` request header."""
        credentials = self._get_credentials(request)
        if credentials:
            return credentials[0]

    def remember(self, request, principal, **kw):
        """ A no-op. This authentication does not provide a protocol for
        remembering the user. Credentials are sent on every request.
        """
        return []

    def forget(self, request):
        """ Returns challenge headers. This should be attached to a response
        to indicate that credentials are required."""

        # TODO: Should we avoid advertising this ?
        return [('WWW-Authenticate', 'Debug')]

    def callback(self, username, request):
        # Username arg is ignored.  Unfortunately _get_credentials winds up
        # getting called twice when authenticated_userid is called.  Avoiding
        # that, however, winds up duplicating logic from the superclass.
        credentials = self._get_credentials(request)

        principals = credentials[1:]
        if self._callback:
            sub_principals = self._callback(credentials[0], request)
            if sub_principals:
                principals.extend(sub_principals)
        return principals

    def _get_credentials(self, request):
        authorization = request.GET.get('authorization', None)
        authorization = request.headers.get('Authorization', authorization)
        if not authorization:
            return None
        try:
            authmeth, auth = authorization.split(' ', 1)
        except ValueError:  # not enough values to unpack
            return None
        if authmeth.lower() != 'debug':
            return None

        return auth.split(' ')
