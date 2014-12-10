from datetime import datetime

from webtest import TestApp

import squirro.common.config
from common import MultiAppRequestWrapper, setup_session, \
    setup_session_user_objects
from squirro.common.dependency import get_injected, register_instance
from squirro.common.testing import AppRequestWrapper, DummyRequests, \
    TestCaseMixin
from squirro.lib.configuration.testing import setup_config_client
from squirro_client.base import SquirroClient

# register configuration and helper methods
config = squirro.common.config.get_test_config('squirro.api.user')
register_instance('config', config)

# import the model and application after everything has been setup
from squirro.api.user.main import app


class TestUserApiMixin(TestCaseMixin):
    """Make sure the Squirro client authentication part works as excepted."""

    def setUp(self):
        register_instance('config', config)

        # register dependencies
        setup_session()
        setup_session_user_objects()

        wrapper = MultiAppRequestWrapper({
            config.get('services', 'cache_cleansing'): DummyRequests(),
            '*': AppRequestWrapper(TestApp(app)),
        })
        register_instance('requests', wrapper)

        register_instance('access_token', 'token03')
        register_instance('refresh_token', 'token04')

        default = True
        values = {
            'sourcer.default-market': {'value': 'en-US'},
            'user.noise-level': {'value': 100},
            'user.timezone': {'value': 'UTC'},
        }
        setup_config_client(default, values)

        # create new client
        self.client = SquirroClient(
            'client01', 'secret01', tenant='tenant01',
            requests=get_injected('requests'))
        self.client.access_token = 'token01'
        self.client.refresh_token = 'token02'

    def test_get_user_data_v0(self):
        """Make sure that user data can be retrieved with the v0 API."""

        # request user data
        ret = self.client.get_user_data('user01', api_version='v0')
        self.assertEqual(ret['email'], 'me@squirro.com')
        self.assertEqual(ret['id'], 'user01')
        self.assertEqual(ret['tenant'], 'tenant01')

        config = ret['config']
        self.assertEqual(config['market'], 'en-US')
        self.assertEqual(config['noise_level'], 1)
        self.assertEqual(config['timezone'], 'UTC')

    def test_get_user_data_v1(self):
        """Make sure that user data can be retrieved with the v1 API."""

        # request user data
        ret = self.client.get_user_data('user01', api_version='v1')

        self.assertEqual(ret['email'], 'me@squirro.com')
        self.assertEqual(ret['id'], 'user01')
        self.assertEqual(ret['tenant'], 'tenant01')

        config = ret['config']
        self.assertEqual(config['market'], 'en-US')
        self.assertEqual(config['noise_level'], 1)
        self.assertEqual(config['timezone'], 'UTC')

        auths = ret['authentications']
        sfauth = auths['salesforce']
        self.assertEqual(sfauth['service_user'], 'sfdc01')
        self.assertEqual(sfauth['display_name'], None)
        self.assertEqual(sfauth['access_token_expires'], None)
        self.assertEqual(sfauth['access_token'], None)
        self.assertEqual(sfauth['access_secret'], None)
        self.assertEqual(sfauth['access_secret_expires'], None)
        self.assertEqual(sfauth['state'], 'ok')
        self.assertEqual(len(auths), 1)

    def test_update_user_data_v0(self):
        """Make sure that user data can be updated with the v0 API."""

        # update user data
        initial = self.client.get_user_data('user01', api_version='v0')
        updates = {'name': 'Squirro'}
        ret = self.client.update_user_data('user01', updates, api_version='v0')
        self.assertEqual(ret, dict(initial, **updates))

    def test_update_user_data_v1(self):
        """Make sure that user data can be updated with the v1 API."""

        # update user data
        initial = self.client.get_user_data('user01', api_version='v1')
        updates = {'name': 'Squirro'}
        ret = self.client.update_user_data('user01', updates, api_version='v1')
        self.assertEqual(ret, dict(initial, **updates))

    def test_delete_authentication_v1(self):
        """Make sure that authentications can be deleted."""

        initial = self.client.get_user_data('user01', api_version='v1')
        assert 'salesforce' in initial['authentications']
        self.client.delete_authentication('user01', 'salesforce')
        updated = self.client.get_user_data('user01', api_version='v1')
        assert updated['authentications'] == {}

    def test_new_grant_v0(self):
        """Make sure that we're able to create/get user grants"""

        initial = self.client.get_user_grants('user01')
        self.assertEqual(initial, {'grants': []})

        # create a grant
        created_grant = self.client.new_grant('user01', 'user')
        self.assertTrue('id' in created_grant)
        self.assertTrue('refresh_token' in created_grant)

        # check that it got created
        updated = self.client.get_user_grants('user01')
        self.assertEqual(len(updated['grants']), 1)
        grant = updated['grants'][0]
        self.assertEqual(grant['type'], 'user')
        self.assertEqual(grant['refresh_token'], created_grant['refresh_token'])
        self.assertEqual(grant['id'], created_grant['id'])

    def test_new_grant_v0_list_scope(self):
        """Make sure that we're able to create user grant with a scope"""

        initial = self.client.get_user_grants('user01')
        self.assertEqual(initial, {'grants': []})

        # create a grant
        created_grant = self.client.new_grant(
            'user01', 'user', project_permissions=['read.items', 'all'])
        self.assertTrue('id' in created_grant)
        self.assertTrue('refresh_token' in created_grant)

        # check that it got created
        updated = self.client.get_user_grants('user01')
        self.assertEqual(len(updated['grants']), 1)
        grant = updated['grants'][0]
        self.assertEqual(grant['type'], 'user')
        self.assertEqual(grant['refresh_token'], created_grant['refresh_token'])
        self.assertEqual(grant['id'], created_grant['id'])
        self.assertEqual(grant['project_permissions'], ['read.items', 'all'])

    def test_new_grant_v0_string_scope(self):
        """Make sure that we're able to create user grant with a scope"""

        initial = self.client.get_user_grants('user01')
        self.assertEqual(initial, {'grants': []})

        # create a grant
        created_grant = self.client.new_grant(
            'user01', 'user', project_permissions='read.items,all')
        self.assertTrue('id' in created_grant)
        self.assertTrue('refresh_token' in created_grant)

        # check that it got created
        updated = self.client.get_user_grants('user01')
        self.assertEqual(len(updated['grants']), 1)
        grant = updated['grants'][0]
        print repr(grant)
        self.assertEqual(grant['type'], 'user')
        self.assertEqual(grant['refresh_token'], created_grant['refresh_token'])
        self.assertEqual(grant['id'], created_grant['id'])
        self.assertEqual(grant['project_permissions'], ['read.items', 'all'])

    def test_delete_grant_v0(self):
        """Check that grants get deleted"""

        initial = self.client.get_user_grants('user01')
        self.assertEqual(initial, {'grants': []})

        # create grant and check it's there
        self.client.new_grant('user01', 'user')
        updated = self.client.get_user_grants('user01')
        self.assertEqual(len(updated['grants']), 1)

        # delete grant and check it's gone
        self.client.delete_grant('user01', updated['grants'][0]['id'])
        updated2 = self.client.get_user_grants('user01')
        self.assertEqual(updated2, {'grants': []})

    def test_new_or_modify_authentication(self):
        """Make sure that new authentications can be created and existing ones
        updated.
        """

        # get user authentications
        initial = self.client.get_user_data('user01', api_version='v1')
        auths = initial['authentications']
        self.assertNotEqual(auths.get('salesforce'), None)

        # create new authentication
        auth = self.client.new_or_modify_authentication(
            'user01', 'facebook', '1234567', 'fb-token', 'fb-secret',
            display_name=u'John Sm\xfcth',
            access_token_expires=datetime(2013, 1, 9, 9, 31, 40, 199217),
            access_secret_expires=datetime(2013, 1, 9, 9, 31, 40, 199217))
        self.assertEqual(auth['service_user'], '1234567')
        self.assertEqual(auth['display_name'], u'John Sm\xfcth')
        self.assertEqual(auth['access_token'], 'fb-token')
        self.assertEqual(auth['access_secret'], 'fb-secret')
        self.assertEqual(auth['access_token_expires'], '2013-01-09T09:31:40')
        self.assertEqual(auth['access_secret_expires'], '2013-01-09T09:31:40')

        # update existing authentication
        auth = self.client.new_or_modify_authentication(
            'user01', 'facebook', '1234567', 'new-fb-token', 'new-fb-secret')
        self.assertEqual(auth['service_user'], '1234567')
        self.assertEqual(auth['access_token'], 'new-fb-token')
        self.assertEqual(auth['access_secret'], 'new-fb-secret')

        # update existing authentication once more
        auth = self.client.new_or_modify_authentication(
            'user01', 'facebook', '1234567', 'new-fb-token', 'new-fb-secret',
            access_token_expires=datetime(2014, 1, 9, 9, 31, 40, 199217),
            access_secret_expires=datetime(2014, 1, 9, 9, 31, 40, 199217))
        self.assertEqual(auth['service_user'], '1234567')
        self.assertEqual(auth['access_token_expires'], '2014-01-09T09:31:40')
        self.assertEqual(auth['access_secret_expires'], '2014-01-09T09:31:40')

    def test_get_authentication(self):
        """Make sure that authentications can be retrieved"""

        # call the previous test to generate a complete authentication
        self.test_new_or_modify_authentication()

        auth = self.client.get_authentication('user01', 'facebook')
        self.assertEqual(auth['display_name'], u'John Sm\xfcth')
        self.assertEqual(auth['service_user'], '1234567')
        self.assertEqual(auth['access_token'], 'new-fb-token')
        self.assertEqual(auth['access_secret'], 'new-fb-secret')
        self.assertEqual(auth['access_token_expires'], '2014-01-09T09:31:40')
        self.assertEqual(auth['access_secret_expires'], '2014-01-09T09:31:40')
