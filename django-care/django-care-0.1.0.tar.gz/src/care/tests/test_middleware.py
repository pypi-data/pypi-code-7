from django.test import TestCase
from mock import sentinel
from smarttest.compat import RequestFactory

from care.middleware import AnnotateSQLMiddleware
from care.models import request_data


class AnnotateSQLMiddlewareProcessRequestTest(TestCase):

    def test_should_set_path(self):
        factory = RequestFactory()
        request = factory.get('/test_path')
        middleware = AnnotateSQLMiddleware()

        middleware.process_request(request)
        self.assertEqual(request_data.path, 'http://testserver/test_path')


class AnnotateSQLMiddlewareProcessViewTest(TestCase):

    def test_should_set_view(self):
        factory = RequestFactory()
        request = factory.get('/test_path')
        middleware = AnnotateSQLMiddleware()
        view_func = self.test_should_set_view

        middleware.process_view(request, view_func, (), {})

        self.assertEqual(request_data.view,
                         'care.tests.test_middleware.test_should_set_view')


class AnnotateSQLMiddlewareProcessResponseTest(TestCase):

    def test_should_clear_path_and_view(self):
        middleware = AnnotateSQLMiddleware()

        middleware.process_response(sentinel.request, sentinel.response)

        self.assertEqual(request_data.path, '')
        self.assertEqual(request_data.view, '')
