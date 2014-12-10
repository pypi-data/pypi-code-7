from squirro.common.testing import TestCaseMixin
from webtest import TestApp
from squirro.common.dependency import register_instance, get_injected
from squirro.common.testing import AppRequestWrapper
from common import setup_session, setup_session_user_objects
from squirro_client.base import SquirroClient
from squirro_client.exceptions import AuthenticationError, InputDataError
import squirro.common.config
from datetime import datetime


# register configuration and helper methods
config = squirro.common.config.get_test_config('squirro.api.user')
register_instance('config', config)

# import the model and application after everything has been setup
from squirro.api.user.main import app


class TestSquirroClient(TestCaseMixin):
    """Make sure the Squirro client authentication part works as excepted."""

    def setUp(self):

        # register dependencies
        setup_session()
        setup_session_user_objects()

        wrapper = AppRequestWrapper(TestApp(app))
        register_instance('requests', wrapper)

        register_instance('access_token', 'token03')
        register_instance('refresh_token', 'token04')

    def test_authentication_invalid(self):
        """Make sure that invalid authentication methods are detected."""

        # create new client
        client = SquirroClient(
            'client01', 'secret01', tenant='tenant01',
            requests=get_injected('requests'))

        # all invalid methods
        methods = [
            {}, {'auth_service': 'salesforce'},
            {'auth_user': 'sfdc01'},
            {'username': 'me@squirro.com'}, {'password': 'test'},
        ]
        for kwargs in methods:
            self.assertRaises(
                AuthenticationError, client.authenticate, **kwargs)

    def test_authenticate_access_token(self):
        """Make sure that authentication by access token works."""

        # create new client
        client = SquirroClient(
            'client01', 'secret01', tenant='tenant01',
            requests=get_injected('requests'))
        client.authenticate(access_token='token01')

        self.assertEqual(client.access_token, 'token01')
        self.assertEqual(client.refresh_token, 'token02')

    def test_authenticate_refresh_token(self):
        """Make sure that authentication by refresh token works."""

        # create new client
        client = SquirroClient(
            'client01', 'secret01', tenant='tenant01',
            requests=get_injected('requests'))
        client.authenticate(refresh_token='token02')

        self.assertEqual(client.access_token, 'token01')
        self.assertEqual(client.refresh_token, 'token02')

    def test_authenticate_ext(self):
        """Make sure that authentication by external identifiers works."""

        # create new client
        client = SquirroClient(
            'client01', 'secret01', tenant='tenant01',
            requests=get_injected('requests'))
        client.authenticate(auth_service='salesforce', auth_user='sfdc01')

        self.assertEqual(client.access_token, 'token03')
        self.assertEqual(client.refresh_token, 'token04')

    def test_authenticate_username_password(self):
        """Make sure that authentication by username / password works."""

        # create new client
        client = SquirroClient(
            'client01', 'secret01',
            requests=get_injected('requests'))
        client.authenticate(
            tenant='tenant01', username='me@squirro.com', password='test')

        self.assertEqual(client.access_token, 'token03')
        self.assertEqual(client.refresh_token, 'token04')

    def test_missing_tenant(self):
        """Make sure that the presence of a tenant is enforced."""

        # create new client
        client = SquirroClient(
            'client01', 'secret01',
            requests=get_injected('requests'))
        client.access_token = 'token01'
        client.refresh_token = 'token02'

        self.assertRaises(
            InputDataError, client._perform_request, 'get', 'url')

    def test_format_date(self):
        """Make sure date formatting works."""

        # create new client
        client = SquirroClient(
            'client01', 'secret01',
            requests=get_injected('requests'))

        tests = [
            (datetime(2013, 1, 9, 9, 31, 40, 199217), '2013-01-09T09:31:40'),
            (None, None)
        ]
        for d, expected in tests:
            out = client._format_date(d)
            self.assertEqual(out, expected)
