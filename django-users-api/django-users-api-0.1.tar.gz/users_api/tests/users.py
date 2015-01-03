from tastypie.test import ResourceTestCase

from django.utils.unittest import skip


class UsersResourceTest(ResourceTestCase):

    fixtures = [
        'users_api_users.json'
    ]

    DETAIL_URL = '/users/%s/'
    LIST_URL = '/users/'

    USER_ID = 1
    USERNAME = 'admin'
    PASSWORD = 'admin'

    ADMIN_RESPONSE = {
        u'username': u'admin',
        u'resourceUri': u'/users/1/',
        u'firstName': u'',
        u'lastName': u'',
        u'isSuperuser': True,
        u'isStaff': True,
        u'email': u'admin@admin.com',
        u'isActive': True
    }

    @property
    def detail_uri(self):
        return self.DETAIL_URL % self.USER_ID

    @property
    def list_uri(self):
        return self.LIST_URL

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
            'username': 'newusers',
            'password': 'newpass'
        }

        response = self.api_client.post(self.detail_uri, data=data)
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
            'username': 'newusers',
            'password': 'newpass'
        }
        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpUnauthorized(response)

    def test_put_detail_unauthenticated(self):
        data = {
            'username': 'newusers',
            'password': 'newpass'
        }
        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpUnauthorized(response)

    def test_delete_detail_unauthenticated(self):
        response = self.api_client.delete(self.detail_uri)
        self.assertHttpUnauthorized(response)

    ###########################################################################
    # UNAUTHORIZED
    ###########################################################################
    def test_post_list_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        data = {
            'username': 'newusers',
            'password': 'newpass'
        }

        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpUnauthorized(response)

    def test_put_detail_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        data = {
            'username': 'newusers',
            'password': 'newpass'
        }

        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpUnauthorized(response)

    def test_delete_detail_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.delete(self.detail_uri)
        self.assertHttpUnauthorized(response)

    ###########################################################################
    # GET
    ###########################################################################
    def test_get_list_superuser(self):
        self.login()

        response = self.api_client.get(self.list_uri)
        self.assertHttpOK(response)
        self.assertValidJSONResponse(response)

        res = self.deserialize(response)
        self.assertEqual(res['meta']['totalCount'], 2)
        self.assertDictContainsSubset(self.ADMIN_RESPONSE, res['objects'][0])

    def test_get_detail_superuser(self):
        self.login()

        response = self.api_client.get(self.detail_uri)
        self.assertHttpOK(response)
        self.assertValidJSONResponse(response)

        res = self.deserialize(response)
        self.assertDictContainsSubset(self.ADMIN_RESPONSE, res)

    def test_get_list_normal_user(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.get(self.list_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['meta']['totalCount'], 2)

    def test_get_detail_normal_user(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.get(self.detail_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertDictContainsSubset(self.ADMIN_RESPONSE, res)

    ###########################################################################
    # POST
    ###########################################################################
    def test_post_list(self):
        self.login()

        data = {
            'username': 'user2',
            'password': 'user2',
            'email': 'user2@admin.com'
        }

        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpCreated(response)

        res = self.deserialize(response)
        self.assertNotIn('password', res)

        resource_uri = res['resourceUri']
        response = self.api_client.get(resource_uri)
        self.assertDictContainsSubset({
            u'username': u'user2',
            u'resourceUri': resource_uri,
            u'firstName': u'',
            u'lastName': u'',
            u'isSuperuser': False,
            u'isStaff': False,
            u'email': u'user2@admin.com',
            u'isActive': True
        }, self.deserialize(response))

    def test_post_list_invalid(self):
        self.login()

        data = {}
        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpBadRequest(response)

        data = {'username': 'user2'}
        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpBadRequest(response)

        data = {'password': 'user2'}
        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpBadRequest(response)

        data = {
            'username': 'user2',
            'password': 'user2',
            'email': 'INVALID_EMAIL'
        }
        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpBadRequest(response)

    ###########################################################################
    # PUT
    ###########################################################################
    def test_put_detail(self):
        self.login()

        data = {
            'firstName': 'Admin',
            'lastName': 'Admin Last'
        }
        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpOK(response)

        self.assertDictContainsSubset(data, self.deserialize(response))

        # Another user
        data = {
            'firstName': 'User 1',
            'lastName': '1 User'
        }
        self.USER_ID = 2
        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpOK(response)

        self.assertDictContainsSubset(data, self.deserialize(response))

    def test_put_detail_superuser_change_password(self):
        self.login()

        self.USER_ID = 2
        data = {
            'password': 'new password'
        }
        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpOK(response)

        self.logout()

        self.USERNAME = 'user1'
        self.PASSWORD = data['password']
        self.login()
        response = self.api_client.get(self.list_uri)
        self.assertHttpOK(response)

    @skip('Required with different authorization')
    def test_put_detail_owner_change_password(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.USER_ID = 2
        self.login()

        data = {
            'password': 'new password'
        }
        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpOK(response)

        self.logout()

        # Try to use old password, and fail!
        self.login()
        response = self.api_client.get(self.list_uri)
        self.assertHttpUnauthorized(response)

    def test_put_detail_invalid(self):
        self.login()

        data = {
            'email': 'INVALID_EMAIL'
        }
        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpBadRequest(response)

    def test_put_detail_not_found(self):
        self.login()

        data = {
            'email': 'INVALID_EMAIL'
        }
        self.USER_ID = 100
        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpBadRequest(response)

    ###########################################################################
    # DELETE
    ###########################################################################
    def test_delete_detail(self):
        self.login()

        self.USER_ID = 2

        response = self.api_client.delete(self.detail_uri)
        self.assertHttpAccepted(response)

    def test_delete_detail_not_found(self):
        self.login()

        self.USER_ID = 200

        response = self.api_client.delete(self.detail_uri)
        self.assertHttpNotFound(response)
