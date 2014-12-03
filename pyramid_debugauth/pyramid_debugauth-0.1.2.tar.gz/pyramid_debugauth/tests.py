import unittest
from webtest import TestApp

from pyramid import testing


class Unittest(unittest.TestCase):
    def _getTargetClass(self):
        from . import DebugAuthenticationPolicy
        return DebugAuthenticationPolicy

    def _makeOne(self):
        return self._getTargetClass()()

    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne())

    def test_header_unauthenticated_userid(self):
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Debug chrisr'
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), 'chrisr')

    def test_header_unauthenticated_userid_no_credentials(self):
        request = testing.DummyRequest()
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_header_unauthenticated_bad_header(self):
        request = testing.DummyRequest()
        request.headers['Authorization'] = '...'
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_header_unauthenticated_userid_not_debug(self):
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Complicated things'
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_header_authenticated_userid(self):
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Debug chrisr'
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), 'chrisr')

    def test_qs_unauthenticated_userid(self):
        request = testing.DummyRequest(params={'authorization': 'debug chrisr'})
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), 'chrisr')

    def test_qs_unauthenticated_userid_no_credentials(self):
        request = testing.DummyRequest(params={})
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_qs_unauthenticated_bad_header(self):
        request = testing.DummyRequest(params={'authorization': '...'})
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_qs_unauthenticated_userid_not_debug(self):
        request = testing.DummyRequest(params={'authorization': 'Complicated'})
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_qs_authenticated_userid(self):
        request = testing.DummyRequest(params={'authorization': 'debug chrisr'})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), 'chrisr')

    def test_remember(self):
        policy = self._makeOne()
        self.assertEqual(policy.remember(None, None), [])

    def test_forget(self):
        policy = self._makeOne()
        self.assertEqual(policy.forget(None), [
            ('WWW-Authenticate', 'Debug')])


class FunctionalTest(unittest.TestCase):
    def get_config(self):
        from pyramid.config import Configurator
        from pyramid.security import Allow
        from pyramid.authorization import ACLAuthorizationPolicy

        from pyramid_debugauth import DebugAuthenticationPolicy

        class Root(object):
            __acl__ = [(Allow, 'bob', 'user_id'),
                       (Allow, 'principal1', 'principal1'),
                       (Allow, 'principal2', 'principal2')]
            def __init__(self, request):
                pass

        config = Configurator(root_factory=Root)
        config.set_authentication_policy(DebugAuthenticationPolicy())
        config.set_authorization_policy(ACLAuthorizationPolicy())
        return config

    def setUp(self):
        config = self.get_config()

        def view(self, request):
            request.response.body = 'OK'
            return request.response

        config.add_route('user_id', '/user_id')
        config.add_view(view, route_name='user_id', permission='user_id')
        config.add_route('principal1', '/principal1')
        config.add_view(view, route_name='principal1', permission='principal1')
        config.add_route('principal2', '/principal2')
        config.add_view(view, route_name='principal2', permission='principal2')

        self.app = TestApp(config.make_wsgi_app())

    def test_forbidden(self):
        self.app.get('/user_id', status=403)
        self.app.get('/principal1', status=403)
        self.app.get('/principal2', status=403)

    def test_header_user_id(self):
        self.app.get('/user_id',
                     headers={'Authorization': 'Debug bob'},
                     status=200)

    def test_header_principal1(self):
        self.app.get('/principal1',
                     headers={'Authorization': 'Debug bob principal1'},
                     status=200)

    def test_header_principal2(self):
        self.app.get('/principal2',
                     headers={'Authorization': 'Debug bob principal2'},
                     status=200)

    def test_qs_user_id(self):
        self.app.get('/user_id',
                     params={'authorization': 'debug bob'},
                     status=200)

    def test_qs_principal1(self):
        self.app.get('/principal1',
                     params={'authorization': 'debug bob principal1'},
                     status=200)

    def test_qs_principal2(self):
        self.app.get('/principal2',
                     params={'authorization': 'debug bob principal2'},
                     status=200)
