from tastypie.test import ResourceTestCase

from django.utils.unittest import skip
from django.contrib.auth.models import Permission


class PermissionsResourceTest(ResourceTestCase):

    fixtures = [
        'users_api_users.json'
    ]

    DETAIL_URL = '/permissions/%s/'
    LIST_URL = '/permissions/'

    USER_PERMS_LIST_URL = '/users/%s/permissions/'
    USER_PERMS_DETAIL_URL = '/users/%s/permissions/%s/'

    GROUP_PERMS_LIST_URL = '/groups/%s/permissions/'
    GROUP_PERMS_DETAIL_URL = '/groups/%s/permissions/%s/'

    PERM_ID = 1

    GROUP_ID = 1

    USER_ID = 1
    USERNAME = 'admin'
    PASSWORD = 'admin'

    PERMISSION = {
        'codename': 'add_logentry',
        'name': 'Can add log entry',
        'contentTypeUri': '/contenttypes/1/',
        'resourceUri': '/permissions/1/'
    }

    @property
    def detail_uri(self):
        return self.DETAIL_URL % self.PERM_ID

    @property
    def user_detail_uri(self):
        return self.USER_PERMS_DETAIL_URL % (self.USER_ID, self.PERM_ID)

    @property
    def group_detail_uri(self):
        return self.GROUP_PERMS_DETAIL_URL % (self.GROUP_ID, self.PERM_ID)

    @property
    def list_uri(self):
        return self.LIST_URL

    @property
    def user_list_uri(self):
        return self.USER_PERMS_LIST_URL % self.USER_ID

    @property
    def group_list_uri(self):
        return self.GROUP_PERMS_LIST_URL % self.GROUP_ID

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
            'codename': 'view_permission',
            'name': 'Can view permission',
            'contentTypeUri': '/contenttypes/1/'
        }

        response = self.api_client.post(self.detail_uri, data=data)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.post(self.user_detail_uri, data=data)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.post(self.group_detail_uri, data=data)
        self.assertHttpMethodNotAllowed(response)

    def test_post_detail_user_group_not_allowed(self):
        self.login()

        data = {
            'codename': 'view_permission',
            'name': 'Can view permission',
            'contentTypeUri': '/contenttypes/1/'
        }

        response = self.api_client.post(self.user_detail_uri, data=data)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.post(self.group_detail_uri, data=data)
        self.assertHttpMethodNotAllowed(response)

    def test_post_list_user_group_not_allowed(self):
        self.login()

        data = {
            'codename': 'view_permission',
            'name': 'Can view permission',
            'contentTypeUri': '/contenttypes/1/'
        }

        response = self.api_client.post(self.user_list_uri, data=data)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.post(self.group_list_uri, data=data)
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
            'codename': 'view_permission',
            'name': 'Can view permission',
            'contentTypeUri': '/contenttypes/1/'
        }
        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpUnauthorized(response)

    def test_put_detail_unauthenticated(self):
        data = {
            'codename': 'view_permission',
            'name': 'Can view permission',
            'contentTypeUri': '/contenttypes/1/'
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
    def test_get_list_user_group_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.get(self.user_list_uri)
        self.assertHttpUnauthorized(response)

    @skip('Required with a more strict authorization')
    def test_get_detail_user_group_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.get(self.user_detail_uri)
        self.assertHttpUnauthorized(response)

        response = self.api_client.get(self.group_detail_uri)
        self.assertHttpUnauthorized(response)

    def test_post_list_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        data = {
            'codename': 'view_permission',
            'name': 'Can view permission',
            'contentTypeUri': '/contenttypes/1/'
        }

        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpUnauthorized(response)

    def test_put_detail_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        data = {
            'codename': 'view_permission',
            'name': 'Can view permission',
            'contentTypeUri': '/contenttypes/1/'
        }

        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpUnauthorized(response)

    def test_delete_detail_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.delete(self.detail_uri)
        self.assertHttpUnauthorized(response)

    def test_delete_detail_user_group_unauthorized(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.delete(self.user_detail_uri)
        self.assertHttpUnauthorized(response)

        response = self.api_client.delete(self.group_detail_uri)
        self.assertHttpUnauthorized(response)

    ###########################################################################
    # GET
    ###########################################################################
    def test_get_list(self):
        self.login()

        response = self.api_client.get(self.list_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['meta']['totalCount'], 18)
        permission = res['objects'][0]
        self.assertIn('codename', permission)
        self.assertIn('name', permission)
        self.assertIn('contentTypeUri', permission)
        self.assertIn('resourceUri', permission)

    def test_get_list_normal_user(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.get(self.list_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['meta']['totalCount'], 18)
        permission = res['objects'][0]
        self.assertIn('codename', permission)
        self.assertIn('name', permission)
        self.assertIn('contentTypeUri', permission)
        self.assertIn('resourceUri', permission)

    def test_get_list_user_group(self):
        self.login()

        response = self.api_client.get(self.user_list_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['meta']['totalCount'], 3)
        permission = res['objects'][0]
        self.assertIn('codename', permission)
        self.assertIn('name', permission)
        self.assertIn('contentTypeUri', permission)
        self.assertIn('resourceUri', permission)

        response = self.api_client.get(self.group_list_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['meta']['totalCount'], 3)
        permission = res['objects'][0]
        self.assertIn('codename', permission)
        self.assertIn('name', permission)
        self.assertIn('contentTypeUri', permission)
        self.assertIn('resourceUri', permission)

    def test_get_list_user_group_normal_user(self):
        self.USER_ID = 2
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.get(self.user_list_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['meta']['totalCount'], 0)

        response = self.api_client.get(self.group_list_uri)
        self.assertHttpOK(response)

        res = self.deserialize(response)
        self.assertEqual(res['meta']['totalCount'], 3)

    def test_get_detail(self):
        self.login()

        response = self.api_client.get(self.detail_uri)
        self.assertHttpOK(response)

        permission = self.deserialize(response)
        self.assertDictContainsSubset(self.PERMISSION, permission)

    def test_get_detail_normal_user(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.get(self.detail_uri)
        self.assertHttpOK(response)

        permission = self.deserialize(response)
        self.assertDictContainsSubset(self.PERMISSION, permission)

    def test_get_detail_user_group(self):
        self.login()

        response = self.api_client.get(self.user_detail_uri)
        self.assertHttpOK(response)

        permission = self.deserialize(response)
        self.assertDictContainsSubset(self.PERMISSION, permission)

        response = self.api_client.get(self.group_detail_uri)
        self.assertHttpOK(response)

        permission = self.deserialize(response)
        self.assertDictContainsSubset(self.PERMISSION, permission)

    def test_get_detail_user_group_normal_user(self):
        self.USERNAME = 'user1'
        self.PASSWORD = 'user1'
        self.login()

        response = self.api_client.get(self.user_detail_uri)
        self.assertHttpOK(response)

        permission = self.deserialize(response)
        self.assertDictContainsSubset(self.PERMISSION, permission)

        response = self.api_client.get(self.group_detail_uri)
        self.assertHttpOK(response)

        permission = self.deserialize(response)
        self.assertDictContainsSubset(self.PERMISSION, permission)

    def test_get_detail_not_found(self):
        self.login()

        self.PERM_ID = 1000
        response = self.api_client.get(self.detail_uri)
        self.assertHttpNotFound(response)

    def test_get_detail_user_group_not_found(self):
        self.login()

        self.PERM_ID = 1000
        response = self.api_client.get(self.user_detail_uri)
        self.assertHttpNotFound(response)

        response = self.api_client.get(self.group_detail_uri)
        self.assertHttpNotFound(response)

    ###########################################################################
    # POST
    ###########################################################################
    def test_post_list(self):
        self.login()

        # Delete first permission
        permission = Permission.objects.get(id=1)
        permission.delete()

        data = {
            'codename': permission.codename,
            'name': permission.name,
            'contentTypeUri': '/contenttypes/%s/' % permission.content_type.id
        }

        response = self.api_client.post(self.list_uri, data=data)
        self.assertHttpCreated(response)

    def test_post_list_invalid(self):
        self.login()

        data = {
            'codename': 'codename',
            'name': 'name',
            'contentTypeUri': '/contenttypes/1/'
        }

        required = ('codename', 'name')

        for field in required:
            # Missing ContentTypeUri will raise early errors by tastypie!
            post_data = data.copy()
            post_data.pop(field)

            response = self.api_client.post(self.list_uri, data=post_data)
            self.assertHttpBadRequest(response)

    ###########################################################################
    # PUT
    ###########################################################################
    def test_put_detail(self):
        self.login()

        data = {
            'codename': 'add_logentry',
            'name': 'Can add NEW log entry',
            'content_type': 1
        }

        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpOK(response)

        permission = self.deserialize(response)
        self.assertEqual(data['name'], permission['name'])

    def test_put_detail_create_new(self):
        """Put detail for non-existing Permission"""
        self.login()

        # Delete first permission
        permission = Permission.objects.get(id=1)
        permission.delete()

        data = {
            'codename': permission.codename,
            'name': permission.name,
            'contentTypeUri': '/contenttypes/%s/' % permission.content_type.id
        }

        response = self.api_client.put(self.detail_uri, data=data)
        self.assertHttpCreated(response)

        permission = self.deserialize(response)
        self.assertDictContainsSubset(data, permission)
        self.assertEqual(permission['resourceUri'], '/permissions/1/')

    def test_put_detail_user_group(self):
        self.login()

        permission = Permission.objects.get(id=1)

        data = {
            'codename': permission.codename,
            'name': permission.name,
            'contentTypeUri': '/contenttypes/%s/' % permission.content_type.id
        }

        response = self.api_client.put(self.user_detail_uri, data=data)
        self.assertHttpOK(response)

        permission = self.deserialize(response)
        self.assertDictContainsSubset(data, permission)

        # Another user
        self.USER_ID = 2
        response = self.api_client.put(self.user_detail_uri, data=data)
        self.assertHttpOK(response)

        permission = self.deserialize(response)
        self.assertDictContainsSubset(data, permission)

        response = self.api_client.put(self.group_detail_uri, data=data)
        self.assertHttpOK(response)

        permission = self.deserialize(response)
        self.assertDictContainsSubset(data, permission)

    ###########################################################################
    # DELETE
    ###########################################################################
    def test_delete_detail(self):
        self.login()

        response = self.api_client.delete(self.detail_uri)
        self.assertHttpAccepted(response)

    def test_delete_detail_not_found(self):
        self.login()

        self.PERM_ID = 1000
        response = self.api_client.delete(self.detail_uri)
        self.assertHttpNotFound(response)

    def test_delete_detail_user_group(self):
        self.login()

        response = self.api_client.delete(self.user_detail_uri)
        self.assertHttpAccepted(response)

        # Another user.
        self.USER_ID = 2

        permission = Permission.objects.get(id=1)

        data = {
            'codename': permission.codename,
            'name': permission.name,
            'contentTypeUri': '/contenttypes/%s/' % permission.content_type.id
        }
        # first, assign permission.
        response = self.api_client.put(self.user_detail_uri, data=data)
        self.assertHttpOK(response)
        # then delete it.
        response = self.api_client.delete(self.user_detail_uri)
        self.assertHttpAccepted(response)

        # group
        response = self.api_client.delete(self.group_detail_uri)
        self.assertHttpAccepted(response)

    def test_delete_detail_user_group_not_found(self):
        self.login()

        self.PERM_ID = 1000
        response = self.api_client.delete(self.user_detail_uri)
        self.assertHttpNotFound(response)

        response = self.api_client.delete(self.group_detail_uri)
        self.assertHttpNotFound(response)
