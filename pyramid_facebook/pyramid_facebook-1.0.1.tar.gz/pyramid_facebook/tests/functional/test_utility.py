import mock

from . import TestView


def dummy_view(request):
    graph_api = request.graph_api
    return {'app_token': graph_api.oauth_token}


class Test(TestView):

    @mock.patch('facepy.get_application_access_token')
    def test_get_application_graph_api(self, m_get_app_token):
        from pyramid_facebook.utility import get_application_graph_api
        m_get_app_token.return_value = 'app_token'

        graph_api1 = get_application_graph_api(self.config.registry)
        graph_api2 = get_application_graph_api(self.config.registry)

        self.assertIs(graph_api1, graph_api2)

    @mock.patch('facepy.get_application_access_token')
    def test_includeme(self, m_get_app_token):
        m_get_app_token.return_value = 'app_token'

        self.config.include('pyramid_facebook.utility')
        self.config.add_route('test', '/test')
        self.config.add_view(dummy_view, route_name='test', renderer='json')

        self.assertEqual(
            {u'app_token': 'app_token'},
            self.app.get('/test').json
            )

    @mock.patch('facepy.get_application_access_token')
    def test_facepy_error(self, m_get_app_token):
        from facepy import FacepyError
        from pyramid_facebook.utility import (
            get_app_token,
            get_application_graph_api,
            )

        m_get_app_token.side_effect = FacepyError('ooops')

        self.assertIsNone(get_app_token(self.config.registry))
        self.assertIsNone(get_application_graph_api(self.config.registry))
