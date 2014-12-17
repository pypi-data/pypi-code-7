import facepy
import mock
from zope.interface import classImplements

from pyramid_facebook.lib import encrypt_signed_request
from pyramid_facebook.utility import IGraphAPI

__all__ = ['conf', 'get_signed_request']

conf = {
    'facebook.app_id': '1234567890',
    'facebook.secret_key': 'abcdef1234567890',
    'facebook.namespace': 'test_canvas',
    'facebook.scope': 'publish_actions,email',
    'facebook.rt-subscriptions': ('\nuser = friends, name\n'
                                  'payments = actions, disputes'),
    'facebook.api_version': 'v1000',
    'pyramid.debug_routematch': True,
    }


def get_signed_request(**params):
    return encrypt_signed_request(conf['facebook.secret_key'], params)


def includeme(config):
    config.add_request_method(_get_app_token, 'fb_app_token', reify=True)
    config.add_request_method(_get_application_graph_api, 'graph_api',
                              reify=True)
    config.add_request_method(_get_graph_api, 'new_graph_api')


def _get_graph_api(request, access_token):
    version = request.registry.settings['facebook.api_version']
    return mock.Mock(spec=facepy.GraphAPI,
                     url='https://graph.facebook.com/' + version)


def _get_app_token(request_or_config):
    return get_app_token(request_or_config.registry)


def _get_application_graph_api(request_or_config):
    return get_application_graph_api(request_or_config.registry)


def get_app_token(registry):
    app_id = registry.settings['facebook.app_id']
    secret_key = registry.settings['facebook.secret_key']
    if registry.settings.get('facebook.app_token') is None:
        registry.settings['facebook.app_token'] = mock.Mock(
            app_id=app_id,
            secret_key=secret_key,
            )
    return registry.settings.get('facebook.app_token')


def get_application_graph_api(registry):
    graph_api = registry.queryUtility(IGraphAPI)
    if graph_api:
        return graph_api

    app_token = get_app_token(registry)
    if app_token is None:
        return None

    classImplements(mock.Mock, IGraphAPI)
    api_version = registry.settings['facebook.api_version']
    api = mock.Mock(spec=facepy.GraphAPI,
                    oauth_token=app_token,
                    url='https://graph.facebook.com/' + api_version)

    registry.registerUtility(api)

    return api
