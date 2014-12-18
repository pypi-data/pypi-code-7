from mxit.oauth import OAuth
from mxit.services import MessagingService, UserService


class Mxit(object):
    """
    Mxit API wrapper
    """

    def __init__(self, client_id, client_secret, redirect_uri=None, state=None, cache=None, verify_cert=True, oauth_provider=None, user_id=None):
        # Auth
        if oauth_provider:
            self.oauth = oauth_provider(client_id, client_secret, user_id, redirect_uri, state, cache, verify_cert)
        else:
            self.oauth = OAuth(client_id, client_secret, redirect_uri, state, cache, verify_cert)

        # Services
        self.messaging = MessagingService(self.oauth)
        self.users = UserService(self.oauth)