from tastypie.test import ResourceTestCase

from django.utils.unittest import skip


class GroupsResourceTest(ResourceTestCase):

    fixtures = [
        'users_api_users.json'
    ]

    DETAIL_URL = '/groups/%s/'
    LIST_URL = '/groups/'

    USER_GROUPS_LIST_URL = '/users/%s/groups/'
    USER_GROUPS_DETAIL_URL = '/users/%s/groups/%s/'

    GROUP_ID = 1

    USER_ID = 1
    USERNAME = 'admin'
    PASSWORD = 'admin'

    @property
    def detail_uri(self):
        return self.DETAIL_URL % self.GROUP_ID

    @property
    def user_detail_uri(self):
        return self.USER_GROUPS_DETAIL_URL % (self.USER_ID, self.GROUP_ID)

    @property
    def list_uri(self):
        return self.LIST_URL

    @property
    def user_list_uri(self):
        return self.USER_GROUPS_LIST_URL % self.USER_ID

    def login(self):
        self.api_client.client.login(username=self.USERNAME,
                                     password=self.PASSWORD)

    def logout(self):
        self.api_client.client.logout()

    ###########################################################################
    # NOT ALLOWED
    ###########################################################################
    def test_delete_list_not_allowed(self):
        self.login()
        response = self.api_client.delete(self.list_uri)
        self.assertHttpMethodNotAllowed(response)

    def test_put_list_not_allowed(self):
        self.login()
        response = self.api_client.put(self.list_uri)
        self.assertHttpMethodNotAllowed(response)

    def test_post_detail_not_allowed(self):
        self.login()

        data = {
            'name': 'newgroup'
        }

        response = self.api_client.post(self.detail_uri, data=data)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.post(self.user_detail_uri, data=data)
        self.assertHttpMethodNotAllowed(response)

    def test_post_detail_user_not_allowed(self):
        self.login()

        data = {
            'name': 'newgroup'
        }

        response = self.api_client.post(self.user_detail_uri, data=data)
        self.assertHttpMethodNotAllowed(response)

    ###########################################################################
    # UNAUTHENTICATED
    ###########################################################################
    def test_get_list_unauthenticated(self):
        response = self.api_client.get(self.list_uri)
        self.assertHttpUnauthorized(response)

    def test_get_detail_unauthenticated(self):
        response = self.api_client.get(self.detail_uri)
        self.assertHttpUnauthorized(response)

    def test_post_list_unauthenticated(self):
        data = {
            'name': 'newgroup'
        }
        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpUnauthorized(response)

    def test_put_detail_unauthenticated(self):
        data = {
            'name': 'newgroup'
        }
        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpUnauthorized(response)

    def test_delete_detail_unauthenticated(self):
        response = self.api_client.delete(self.detail_uri)
        self.assertHttpUnauthorized(response)

    ###########################################################################
    # UNAUTHORIZED
    ###########################################################################
    @skip('Required with a more strict authorization')
    def test_get_list_user_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.get(self.user_list_uri)
        self.assertHttpUnauthorized(response)

    @skip('Required with a more strict authorization')
    def test_get_detail_user_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.get(self.user_detail_uri)
        self.assertHttpUnauthorized(response)

    def test_post_list_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        data = {
            'name': 'newgroup'
        }

        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpUnauthorized(response)

    def test_put_detail_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        data = {
            'name': 'newgroup'
        }

        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpUnauthorized(response)

    def test_delete_detail_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.delete(self.detail_uri)
        self.assertHttpUnauthorized(response)

    def test_delete_detail_user_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.delete(self.user_detail_uri)
        self.assertHttpUnauthorized(response)

    ###########################################################################
    # GET
    ###########################################################################
    def test_get_list(self):
        self.login()

        response = self.api_client.get(self.list_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['meta']['totalCount'], 3)
        self.assertDictContainsSubset(
            {
                'name': 'Group1',
                'resourceUri': '/groups/1/'
            }, res['objects'][0])

    def test_get_list_user(self):
        self.login()

        response = self.api_client.get(self.user_list_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['meta']['totalCount'], 2)
        self.assertEqual(res['objects'][0]['name'], 'Group1')
        self.assertEqual(res['objects'][1]['name'], 'Group2')

        # Another user
        self.USER_ID = 2
        response = self.api_client.get(self.user_list_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['meta']['totalCount'], 1)
        self.assertEqual(res['objects'][0]['name'], 'Group1')

    def test_get_list_normal_user(self):
        self.USER_ID = 2
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.get(self.list_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['meta']['totalCount'], 3)

    def test_get_detail(self):
        self.login()

        response = self.api_client.get(self.detail_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertDictContainsSubset(
            {
                'name': 'Group1',
                'resourceUri': '/groups/1/'
            }, res)

        # Group2
        self.GROUP_ID = 2

        response = self.api_client.get(self.detail_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertDictContainsSubset(
            {
                'name': 'Group2',
                'resourceUri': '/groups/2/'
            }, res)

    def test_get_detail_user(self):
        self.login()

        response = self.api_client.get(self.user_detail_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['name'], 'Group1')

        # Another user
        self.USER_ID = 2
        response = self.api_client.get(self.user_detail_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['name'], 'Group1')

    def test_get_detail_user_normal_user(self):
        self.USER_ID = 2
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.get(self.user_detail_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['name'], 'Group1')

    def test_get_detail_not_found(self):
        self.login()

        self.GROUP_ID = 10
        response = self.api_client.get(self.detail_uri)
        self.assertHttpNotFound(response)

    def test_get_detail_user_not_found(self):
        self.login()

        self.GROUP_ID = 10
        response = self.api_client.get(self.user_detail_uri)
        self.assertHttpNotFound(response)

        # User not found
        self.GROUP_ID = 1
        self.USER_ID = 100
        response = self.api_client.get(self.user_detail_uri)
        self.assertHttpNotFound(response)

    ###########################################################################
    # POST
    ###########################################################################
    def test_post_list(self):
        self.login()

        data = {
            'name': 'Group4'
        }

        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpCreated(response)

        res = self.deserialize(response)
        self.assertDictContainsSubset(
            {
                'name': 'Group4',
                'resourceUri': '/groups/4/'
            }, res)

    def test_post_list_invalid(self):
        self.login()

        data = {}

        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpBadRequest(response)

        data = {
            'group_id': 3
        }

        # Not the valid uri
        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpBadRequest(response)

    ###########################################################################
    # PUT
    ###########################################################################
    def test_put_detail(self):
        self.login()

        data = {
            'name': 'New Name'
        }
        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpOK(response)

        self.assertEqual(data['name'], self.deserialize(response)['name'])

    def test_put_detail_create_new(self):
        self.login()

        data = {
            'name': 'New group name'
        }

        self.GROUP_ID = 100
        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpCreated(response)

        group = self.deserialize(response)
        data['resourceUri'] = '/groups/100/'
        self.assertDictContainsSubset(data, group)

    def test_put_detail_invalid(self):
        self.login()

        data = {}

        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpBadRequest(response)

    def test_put_detail_user(self):
        """Assign group to user."""
        self.login()

        data = {
            'name': 'Group2'
        }

        self.USER_ID = 2
        self.GROUP_ID = 2
        response = self.api_client.put(self.user_detail_uri, data=data)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertDictContainsSubset(
            {
                'name': 'Group2',
                'resourceUri': '/groups/2/'
            }, res)

        # Check if user has the group
        self.GROUP_ID = 2
        response = self.api_client.get(self.user_detail_uri)
        self.assertHttpOK(response)
        self.assertEqual('Group2', self.deserialize(response)['name'])

    ###########################################################################
    # DELETE
    ###########################################################################
    def test_delete_detail(self):
        self.login()

        response = self.api_client.delete(self.detail_uri)
        self.assertHttpAccepted(response)

        response = self.api_client.get(self.detail_uri)
        self.assertHttpNotFound(response)

    def test_delete_detail_user(self):
        """UnAssign group from User"""
        self.login()

        self.USER_ID = 2
        response = self.api_client.delete(self.user_detail_uri)
        self.assertHttpAccepted(response)

        response = self.api_client.get(self.user_detail_uri)
        self.assertHttpNotFound(response)

    def test_delete_detail_not_found(self):
        self.login()

        self.GROUP_ID = 100
        response = self.api_client.delete(self.detail_uri)
        self.assertHttpNotFound(response)

        # User not found
        self.GROUP_ID = 1
        self.USER_ID = 100
        response = self.api_client.delete(self.user_detail_uri)
        self.assertHttpNotFound(response)
