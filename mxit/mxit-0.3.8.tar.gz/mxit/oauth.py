import urllib
from requests import post
from requests.auth import HTTPBasicAuth
from mxit import settings
from mxit.exceptions import MxitAPIParameterException, MxitAPIException


class OAuth():
    """
    Assists with retrieval of OAuth tokens
    """

    def __init__(self, client_id, client_secret, redirect_uri=None, state=None, cache=None, verify_cert=True):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__redirect_uri = redirect_uri
        self.__state = state

        self.__user_token = None
        self.__app_token = None

        self.__cache = cache
        self.__verify_cert = verify_cert

    def __set_user_token(self, scope_string, token):

        if not self.__user_token:
            self.__user_token = {}

        self.__user_token[scope_string] = token
        for scope in scope_string.split():
            self.__user_token[scope] = token

    def __get_user_token(self, scope):
        if self.__user_token and scope in self.__user_token:
            return self.__user_token[scope]
        return None

    def __set_app_token(self, scope_string, token):

        if not self.__app_token:
            self.__app_token = {}

        self.__app_token[scope_string] = token
        for scope in scope_string.split():
            self.__app_token[scope] = token

    def __get_app_token(self, scope):
        if self.__app_token and scope in self.__app_token:
            return self.__app_token[scope]
        return None

    def __user_token_cache_key(self, scope):
        return str("oauth_user_%s_%s" % (scope.replace("/", "_"), self.__client_id))

    def __app_token_cache_key(self, scope):
        return str("oauth_app_%s_%s" % (scope.replace("/", "_"), self.__client_id))

    def auth_url(self, scope):
        """Gets the url a user needs to access to give up a user token"""
        params = {
            'response_type': 'code',
            'client_id': self.__client_id,
            'redirect_uri': self.__redirect_uri,
            'scope': scope
        }

        if self.__state is not None:
            params['state'] = self.__state

        return settings.AUTH_ENDPOINT + '/authorize?' + urllib.urlencode(params)

    def get_user_token(self, scope, code=None):
        """Gets the auth token from a user's response"""

        user_token = self.__get_user_token(scope)

        if user_token:
            return user_token

        if self.__cache is not None:
            token = self.__cache.get(self.__user_token_cache_key())
            if token:
                return token

        if self.__redirect_uri is None or code is None:
            raise MxitAPIParameterException()

        self.__user_token = None

        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.__redirect_uri
        }

        url = settings.AUTH_ENDPOINT + '/token'
        r = post(url, data=payload, auth=HTTPBasicAuth(self.__client_id, self.__client_secret), verify=self.__verify_cert)
        if r.status_code == 200:
            data = r.json()
            self.__set_user_token(scope, data[u'access_token'])
            if self.__cache is not None:
                self.__cache.set(self.__user_token_cache_key(scope), str(data[u'access_token']),
                                 data[u'expires_in'] - 300)

        user_token = self.__get_user_token(scope)

        if not user_token:
            raise MxitAPIException("Failed to retrieve user token for '%s' scope" % scope)

        return user_token

    def get_app_token(self, scope):
        """Gets the app auth token"""

        app_token = self.__get_app_token(scope)

        if app_token:
            return app_token

        if self.__cache is not None:
            token = self.__cache.get(self.__app_token_cache_key(scope))
            if token:
                return token

        self.__app_token = None

        payload = {
            'grant_type': 'client_credentials',
            'scope': scope
        }

        url = settings.AUTH_ENDPOINT + '/token'
        r = post(url, data=payload, auth=HTTPBasicAuth(self.__client_id, self.__client_secret), verify=self.__verify_cert)
        if r.status_code == 200:
            data = r.json()
            self.__set_app_token(scope, data[u'access_token'])
            if self.__cache is not None:
                self.__cache.set(self.__app_token_cache_key(scope), str(data[u'access_token']),
                                 data[u'expires_in'] - 300)

        app_token = self.__get_app_token(scope)

        if not app_token:
            raise MxitAPIException("Failed to retrieve app token for '%s' scope" % scope)

        return app_token
