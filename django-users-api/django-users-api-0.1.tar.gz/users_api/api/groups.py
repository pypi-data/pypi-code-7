from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.validation import Validation
from tastypie.resources import ModelResource
from tastypie.exceptions import ImmediateHttpResponse

from tastypie.http import HttpNotFound, HttpMethodNotAllowed

from django.conf.urls import url
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group

from users_api.common import CommonMeta


class GroupsResourceValidation(Validation):
    def is_valid(self, bundle, request=None):
        request = bundle.request
        errors = {}

        if request.method in ('PUT', 'POST') and 'name' not in bundle.data:
            errors['name'] = 'Required field missing.'

        return errors


class GroupsResource(ModelResource):
    """
    Django Groups RESTful API. This resource enables:
        - Create a new group
        - List existing group(s)
        - Update existing group
        - Delete existing group
        - Assign/Remove groups to/from users

    User should have sufficient privilege to perform any action.

    Available URIs
        - '/groups/'
        - '/groups/<pk>/'
        - '/users/<user_id>/groups/'
        - '/users/<user_id>/groups/<pk>/'
    """
    group_id = fields.IntegerField(null=True)

    class Meta(CommonMeta):
        queryset = Group.objects.all()
        excludes = ['id', 'group_id']

        validation = GroupsResourceValidation()

    def full_dehydrate(self, bundle, **kwargs):
        """
        Avoid returning excluded fields when always_return_data is True.

        Issue: https://github.com/toastdriven/django-tastypie/issues/654
        """
        bundle.data = {}
        bundle = super(GroupsResource, self).full_dehydrate(bundle, **kwargs)
        for field in self._meta.excludes:
            if field in bundle.data:
                del bundle.data[field]
        return bundle

    def get_user_groups(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user_bundle = self.build_bundle(obj=user, request=bundle.request)

        # Check if request.user is authorized to read this user.
        self.authorized_read_detail(user, user_bundle)

        group_id = kwargs.get('pk')

        if group_id:
            groups = user.groups.filter(id=group_id)
            if not groups:
                raise ImmediateHttpResponse(
                    HttpNotFound('Cannot find user permission!'))

            return groups[0]

        return user.groups.all()

    def assign_group_to_user(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user_bundle = self.build_bundle(obj=user, request=bundle.request)

        # Check if request.user is authorized to change this user.
        self.authorized_update_detail(user, user_bundle)

        group_id = kwargs.get('pk')
        group = get_object_or_404(Group, id=group_id)

        user.groups.add(group)
        user.save()

        bundle.obj = group
        return bundle

    def remove_group_from_user(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user_bundle = self.build_bundle(obj=user, request=bundle.request)

        # Check if request.user is authorized to change this user.
        self.authorized_update_detail(user, user_bundle)

        group_id = kwargs.get('pk')

        groups = user.groups.filter(id=group_id)
        if not groups:
            raise ImmediateHttpResponse(
                HttpNotFound('Cannot find user group!'))

        user.groups.remove(groups[0])
        user.save()

    def obj_get(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')

        if user_id:
            return self.get_user_groups(bundle, **kwargs)

        return super(GroupsResource, self).obj_get(bundle, **kwargs)

    def obj_get_list(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')

        if user_id:
            return self.get_user_groups(bundle, **kwargs)

        return super(GroupsResource, self).obj_get_list(bundle, **kwargs)

    def obj_create(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')

        if user_id:
            raise ImmediateHttpResponse(HttpMethodNotAllowed())

        return super(GroupsResource, self).obj_create(bundle, **kwargs)

    def obj_update(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')

        if user_id:
            return self.assign_group_to_user(bundle, **kwargs)

        return super(GroupsResource, self).obj_update(bundle, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        user_id = kwargs.get('user_id')

        if user_id:
            return self.remove_group_from_user(bundle, **kwargs)

        return super(GroupsResource, self).obj_delete(bundle, **kwargs)

    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        return [
            url(r'^(?P<resource_name>%s)%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_list'),
                name='api_dispatch_list'),
            url(r'^(?P<resource_name>%s)/schema%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_schema'),
                name='api_get_schema'),
            url(r'^(?P<resource_name>%s)/set/(?P<%s_list>[1-9][0-9]*)%s$' %
                (self._meta.resource_name, self._meta.detail_uri_name,
                    trailing_slash()),
                self.wrap_view('get_multiple'),
                name='api_get_multiple'),
            url(r'^(?P<resource_name>%s)/(?P<%s>[1-9][0-9]*)%s$' %
                (self._meta.resource_name, self._meta.detail_uri_name,
                    trailing_slash()),
                self.wrap_view('dispatch_detail'),
                name='api_dispatch_detail'),
        ]

    def prepend_urls(self):
        return [
            url(r'^users/(?P<user_id>[1-9][0-9]*)/groups/$',
                self.wrap_view('dispatch_list'),
                name='api_users_groups_dispatch_list'),
            url(r'^users/(?P<user_id>[1-9][0-9]*)/groups/'
                '(?P<pk>[1-9][0-9]*)/$',
                self.wrap_view('dispatch_detail'),
                name='api_users_groups_dispatch_detail')
        ]
