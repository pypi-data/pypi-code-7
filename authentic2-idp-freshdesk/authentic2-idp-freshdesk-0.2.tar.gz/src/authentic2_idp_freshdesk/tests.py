from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth import get_user_model

class TestDiverter():
    def should_divert(self, user):
        if user.email == 'foobar@example.com':
            return True
        else:
            return False

    def divert_url(self, user, request):
        return request.build_absolute_uri('/'+user.email)


@override_settings(
    AUTHENTICATION_BACKENDS=('authentic2.backends.ModelBackend',),
    FRESHDESK_URL='http://fresh.example.com')
class FreshDeskDiversion(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user(username='foobar', password='foobar',
                                 email='foobar@example.com')

        User.objects.create_user(username='another', password='another',
                                 email='another@example.com')

    @override_settings(FRESHDESK_DIVERT=TestDiverter())
    def test_diversion_configured_diverted(self):
        self.client.login(username='foobar', password='foobar')
        resp = self.client.get('/idp/freshdesk/login/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'],
                         'http://testserver/foobar@example.com')

    @override_settings(FRESHDESK_DIVERT=TestDiverter())
    def test_diversion_configured_not_diverted(self):
        self.client.login(username='another', password='another')
        resp = self.client.get('/idp/freshdesk/login/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('http://fresh.example.com/login/sso?', resp['Location'])

    def test_diversion_not_configured(self):
        self.client.login(username='foobar', password='foobar')
        resp = self.client.get('/idp/freshdesk/login/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('http://fresh.example.com/login/sso?', resp['Location'])
