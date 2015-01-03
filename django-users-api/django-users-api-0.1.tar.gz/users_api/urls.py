from django.conf.urls import patterns, include, url

from users_api.common import UsersApi
from users_api.api.users import UsersResource
from users_api.api.groups import GroupsResource
from users_api.api.permissions import PermissionsResource, ContentTypesResource


django_users_api = UsersApi()

django_users_api.register(GroupsResource())
django_users_api.register(PermissionsResource())
django_users_api.register(ContentTypesResource())
django_users_api.register(UsersResource())

urlpatterns = patterns(
    '',
    url(r'', include(django_users_api.urls)),
)
