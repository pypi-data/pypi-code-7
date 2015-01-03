from tastypie import fields
from tastypie.validation import Validation
from tastypie.resources import ModelResource
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpNotFound, HttpMethodNotAllowed

from django.conf.urls import url
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Permission, ContentType, Group, User

from users_api.common import CommonMeta


class ContentTypesResource(ModelResource):

    class Meta(CommonMeta):
        queryset = ContentType.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']


class PermissionsResourceValidation(Validation):
    def is_valid(self, bundle, request=None):
        request = bundle.request
        errors = {}

        required_fields = ('codename', 'name')

        if request.method == 'POST':
            for field in required_fields:
                if field not in bundle.data:
                    errors[field] = 'Required field missing.'

        return errors


class PermissionsResource(ModelResource):
    """
    Django Permissions RESTful API. This resource enables:
        - Create a new permission
        - List existing permission(s)
        - Update existing permission
        - Delete existing permission
        - Assign/Remove permissions to/from users
        - Assign/Remove permissions to/from groups

    User should have sufficient privilege to perform any action.
    """

    content_type_uri = fields.ToOneField(to=ContentTypesResource,
                                         attribute='content_type')

    class Meta(CommonMeta):
        queryset = Permission.objects.all()

        validation = PermissionsResourceValidation()

    def full_dehydrate(self, bundle, **kwargs):
        """
        Avoid returning excluded fields when always_return_data is True.

        Issue: https://github.com/toastdriven/django-tastypie/issues/654
        """
        bundle.data = {}
        bundle = super(PermissionsResource, self).full_dehydrate(
            bundle, **kwargs)
        for field in self._meta.excludes:
            if field in bundle.data:
                del bundle.data[field]
        return bundle

    def _get_user_permissions(self, bundle, **kwargs):

        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user_bundle = self.build_bundle(obj=user, request=bundle.request)

        # Check if request.user is authorized to read this user.
        self.authorized_read_detail(user, user_bundle)

        permission_id = kwargs.get('pk')

        if permission_id:
            permissions = user.user_permissions.filter(id=permission_id)
            if not permissions:
                raise ImmediateHttpResponse(
                    HttpNotFound('Cannot find user permission!'))

            return permissions[0]

        return user.user_permissions.all()

    def _get_group_permissions(self, bundle, **kwargs):
        group_id = kwargs.get('group_id')
        group = get_object_or_404(Group, id=group_id)
        group_bundle = self.build_bundle(obj=group, request=bundle.request)

        # Check if request.user is authorized to read this group.
        self.authorized_read_detail(group, group_bundle)

        permission_id = kwargs.get('pk')

        if permission_id:
            permissions = group.permissions.filter(id=permission_id)
            if not permissions:
                raise ImmediateHttpResponse(
                    HttpNotFound('Cannot find permission!'))

            return permissions[0]

        return group.permissions.all()

    def _assign_permission_to_user(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user_bundle = self.build_bundle(obj=user, request=bundle.request)

        # Check if request.user is authorized to change this user.
        self.authorized_update_detail(user, user_bundle)

        permission_id = kwargs.get('pk')
        permission = get_object_or_404(Permission, id=permission_id)

        user.user_permissions.add(permission)
        user.save()

        bundle.obj = permission
        return bundle

    def _assign_permission_to_group(self, bundle, **kwargs):
        """Permission should already exist in DB"""

        group_id = kwargs.get('group_id')
        group = get_object_or_404(Group, id=group_id)
        group_bundle = self.build_bundle(obj=group, request=bundle.request)

        # Check if request.user is authorized to change this group.
        self.authorized_update_detail(group, group_bundle)

        permission_id = kwargs.get('pk')
        permission = get_object_or_404(Permission, id=permission_id)

        group.permissions.add(permission)
        group.save()

        bundle.obj = permission
        return bundle

    def _remove_permission_from_user(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user_bundle = self.build_bundle(obj=user, request=bundle.request)

        # Check if request.user is authorized to change this user.
        self.authorized_update_detail(user, user_bundle)

        permission_id = kwargs.get('pk')

        permissions = user.user_permissions.filter(id=permission_id)
        if not permissions:
            raise ImmediateHttpResponse(
                HttpNotFound('Cannot find user permission!'))

        user.user_permissions.remove(permissions[0])
        user.save()

    def _remove_permission_from_group(self, bundle, **kwargs):
        group_id = kwargs.get('group_id')
        group = get_object_or_404(Group, id=group_id)
        group_bundle = self.build_bundle(obj=group, request=bundle.request)

        # Check if request.user is authorized to change this group.
        self.authorized_update_detail(group, group_bundle)

        permission_id = kwargs.get('pk')

        permissions = group.permissions.filter(id=permission_id)
        if not permissions:
            raise ImmediateHttpResponse(
                HttpNotFound('Cannot find user permission!'))

        group.permissions.remove(permissions[0])
        group.save()

    def obj_get(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')
        group_id = kwargs.get('group_id')

        if user_id:
            return self._get_user_permissions(bundle, **kwargs)
        elif group_id:
            return self._get_group_permissions(bundle, **kwargs)

        return super(PermissionsResource, self).obj_get(bundle, **kwargs)

    def obj_get_list(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')
        group_id = kwargs.get('group_id')

        if user_id:
            return self._get_user_permissions(bundle, **kwargs)
        elif group_id:
            return self._get_group_permissions(bundle, **kwargs)

        return super(PermissionsResource, self).obj_get_list(bundle, **kwargs)

    def obj_create(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')
        group_id = kwargs.get('group_id')

        if user_id or group_id:
            raise ImmediateHttpResponse(HttpMethodNotAllowed())

        return super(PermissionsResource, self).obj_create(bundle, **kwargs)

    def obj_update(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')
        group_id = kwargs.get('group_id')

        if user_id:
            return self._assign_permission_to_user(bundle, **kwargs)
        elif group_id:
            return self._assign_permission_to_group(bundle, **kwargs)

        return super(PermissionsResource, self).obj_update(bundle, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')
        group_id = kwargs.get('group_id')

        if user_id:
            return self._remove_permission_from_user(bundle, **kwargs)
        elif group_id:
            return self._remove_permission_from_group(bundle, **kwargs)

        return super(PermissionsResource, self).obj_delete(bundle, **kwargs)

    def prepend_urls(self):
        return [
            url(r'^groups/(?P<group_id>[1-9][0-9]*)/permissions/$',
                self.wrap_view('dispatch_list'),
                name='api_group_permissions_list'),
            url(r'^groups/(?P<group_id>[1-9][0-9]*)/permissions/'
                '(?P<pk>[1-9][0-9]*)/$',
                self.wrap_view('dispatch_detail'),
                name='api_group_permissions_detail'),
            url(r'^users/(?P<user_id>[1-9][0-9]*)/permissions/$',
                self.wrap_view('dispatch_list'),
                name='api_user_permissions_list'),
            url(r'^users/(?P<user_id>[1-9][0-9]*)/permissions/'
                '(?P<pk>[1-9][0-9]*)/$',
                self.wrap_view('dispatch_detail'),
                name='api_user_permissions_detail')
        ]
