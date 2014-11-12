from django.conf import settings
from oauth_tokens.models import AccessToken, AccessTokenGettingError, AccessTokenRefreshingError
from ssl import SSLError
from odnoklassniki import api, OdnoklassnikiError
from simplejson.decoder import JSONDecodeError
from time import sleep
import time
import logging

__all__ = ['api_call']

log = logging.getLogger('odnoklassniki_api')

#TIMEOUT = getattr(settings, 'VKONTAKTE_ADS_REQUEST_TIMEOUT', 1)
ACCESS_TOKEN = getattr(settings, 'ODNOKLASSNIKI_API_ACCESS_TOKEN', None)

APPLICATION_PUBLIC = getattr(settings, 'OAUTH_TOKENS_ODNOKLASSNIKI_CLIENT_PUBLIC', '')
APPLICATION_SECRET = getattr(settings, 'OAUTH_TOKENS_ODNOKLASSNIKI_CLIENT_SECRET', '')

#VkontakteError = odnoklassniki.VKError

class NoActiveTokens(Exception):
    pass

def refresh_tokens(count=1):
    if ACCESS_TOKEN:
        update_tokens()
    else:
        try:
            return AccessToken.objects.refresh('odnoklassniki')
        except AccessTokenRefreshingError, e:
            if count <= 5:
                time.sleep(1)
                refresh_tokens(count+1)
            else:
                raise

def update_tokens(count=1):
    '''
    Update token from provider and return it
    '''
    try:
        return AccessToken.objects.fetch('odnoklassniki')
    except AccessTokenGettingError, e:
        if count <= 5:
            time.sleep(1)
            update_tokens(count+1)
        else:
            raise

def get_api(used_access_tokens=None, *args, **kwargs):
    '''
    Return API instance with latest token from database
    '''
    if ACCESS_TOKEN:
        token = ACCESS_TOKEN
    else:
#        tokens = AccessToken.objects.filter_active_tokens_of_provider('odnoklassniki', *args, **kwargs)
        tokens = AccessToken.objects.filter(provider='odnoklassniki', *args, **kwargs).order_by('-id')
        if used_access_tokens:
            tokens = tokens.exclude(access_token__in=used_access_tokens)

        if len(tokens) == 0:
            raise NoActiveTokens("There is no active AccessTokens with args %s and kwargs %s" % (args, kwargs))
        else:
            token = tokens[0].access_token

    return api.Odnoklassniki(application_key=APPLICATION_PUBLIC, application_secret=APPLICATION_SECRET, token=token)

def api_call(method, recursion_count=0, methods_access_tag=None, used_access_tokens=None, **kwargs):
    '''
    Call API using access_token
    '''
    try:
        api = get_api(tag=methods_access_tag, used_access_tokens=used_access_tokens)
    except NoActiveTokens, e:
        if used_access_tokens:
            # we should wait 1 sec and repeat with clear attribute used_access_tokens
            log.warning("Waiting 1 sec, because all active tokens are used, method: %s, recursion count: %d" % (method, recursion_count))
            time.sleep(1)
            return api_call(method, recursion_count+1, methods_access_tag, used_access_tokens=None, **kwargs)
        else:
            log.warning("Suddenly updating tokens, because no active access tokens and used_access_tokens empty, method: %s, recursion count: %d" % (method, recursion_count))
            update_tokens()
            return api_call(method, recursion_count+1, methods_access_tag, **kwargs)

    try:
        response = api._get(method, **kwargs)
    except OdnoklassnikiError, e:
        if e.code == 102:
            refresh_tokens()
            return api_call(method, recursion_count+1, methods_access_tag, **kwargs)
        if e.code == 2:
            # SERVICE : Service is temporary unavailable., logged by ID :
            sleep(1)
            return api_call(method, recursion_count+1, methods_access_tag, **kwargs)
        elif e.code is None and e.message == 'HTTP error':
            time.sleep(1)
            return api_call(method, recursion_count+1, methods_access_tag, **kwargs)
        else:
            raise
    except (SSLError, JSONDecodeError), e:
        log.error("Exception: '%s' registered while executing method %s with params %s, recursion count: %d" % (e, method, kwargs, recursion_count))
        return api_call(method, recursion_count+1, methods_access_tag, **kwargs)
    except Exception, e:
        log.error("Unhandled error: %s registered while executing method %s with params %s" % (e, method, kwargs))
        raise

    return response
