from tastypie.utils import trailing_slash
from tastypie.validation import Validation
from tastypie.resources import ModelResource

from django.conf.urls import url
from django.contrib.auth.models import User
from django.core.validators import validate_email, ValidationError

from users_api.common import CommonMeta


class UsersResourceValidation(Validation):
    def is_valid(self, bundle, request=None):
        request = bundle.request
        errors = {}

        if request.method == 'POST':
            required_fields = ['username', 'password']
            for field in required_fields:
                if field not in bundle.data:
                    errors[field] = 'Required field missing.'

        if request.method in ['POST', 'PUT'] and 'email' in bundle.data:
            try:
                validate_email(bundle.data['email'])
            except ValidationError:
                errors['email'] = 'Invalid email.'

        return errors


class UsersResource(ModelResource):

    class Meta(CommonMeta):
        queryset = User.objects.all()
        excludes = ['id', 'password']

        validation = UsersResourceValidation()

    def full_dehydrate(self, bundle, **kwargs):
        """
        Avoid returning excluded fields when always_return_data is True.
        This avoids returning the ``password`` after creating/updating a user.

        Issue: https://github.com/toastdriven/django-tastypie/issues/654
        """
        bundle.data = {}
        return super(UsersResource, self).full_dehydrate(bundle, **kwargs)

    def save_password(self, bundle, password):
        bundle.obj.set_password(password)
        bundle.obj.save()

    def obj_create(self, bundle, **kwargs):
        """
        Override to set valid password.
        """
        password = bundle.data.get('password')

        bundle = super(UsersResource, self).obj_create(bundle, **kwargs)

        self.save_password(bundle, password)

        return bundle

    def obj_update(self, bundle, **kwargs):
        """
        Override for password update.
        """
        password = bundle.data.get('password')

        bundle = super(UsersResource, self).obj_update(bundle, **kwargs)

        if password:
            # Requires password update
            self.save_password(bundle, password)

        return bundle

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
