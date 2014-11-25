import logging

import facepy

from zope.interface import classImplements, Interface

log = logging.getLogger(__name__)


def includeme(config):
    config.add_request_method(_get_app_token, 'fb_app_token', reify=True)
    config.add_request_method(_get_application_graph_api, 'graph_api',
                              reify=True)


def _get_app_token(request_or_config):
    return get_app_token(request_or_config.registry)


def _get_application_graph_api(request_or_config):
    return get_application_graph_api(request_or_config.registry)


def get_app_token(registry):
    """Return facebook app token or None if it failed getting it.

    It avoids querying app token each time as fb app token changed only if
    secret key is reseted
    """
    app_id = registry.settings['facebook.app_id']
    secret_key = registry.settings['facebook.secret_key']
    if registry.settings.get('facebook.app_token') is None:
        try:
            token = facepy.get_application_access_token(app_id, secret_key)
        except facepy.FacepyError:
            log.warning('fail to load fb app token')
        else:
            registry.settings['facebook.app_token'] = token
    return registry.settings.get('facebook.app_token')


def get_application_graph_api(registry):
    """
    token.
    """
    graph_api = registry.queryUtility(IGraphAPI)
    if graph_api:
        return graph_api

    app_token = get_app_token(registry)
    if app_token is None:
        return None

    classImplements(facepy.GraphAPI, IGraphAPI)

    api = facepy.GraphAPI(app_token)

    registry.registerUtility(api)

    return api


class IGraphAPI(Interface):
    "Interface to register facepy.GraphAPI to pyramid registry"
