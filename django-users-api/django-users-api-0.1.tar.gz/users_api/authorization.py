from tastypie.exceptions import Unauthorized
from tastypie.authorization import Authorization, DjangoAuthorization


class UsersDjangoAuthorization(DjangoAuthorization):

    def update_detail(self, object_list, bundle):
        if bundle.request.user.id == bundle.obj.id:
            return True
        return super(UsersDjangoAuthorization, self).update_detail(
            object_list, bundle)


class AdminOnlyAuthorization(Authorization):

    def _is_authorized_list(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return object_list
        raise Unauthorized('Admin only access.')

    def _is_authorized_detail(self, object_list, bundle):
        return bundle.request.user.is_superuser

    def read_list(self, object_list, bundle):
        return self._is_authorized_list(object_list, bundle)

    def read_detail(self, object_list, bundle):
        return self._is_authorized_detail(object_list, bundle)

    def create_list(self, object_list, bundle):
        return self._is_authorized_list(object_list, bundle)

    def create_detail(self, object_list, bundle):
        return self._is_authorized_detail(object_list, bundle)

    def update_list(self, object_list, bundle):
        return self._is_authorized_list(object_list, bundle)

    def update_detail(self, object_list, bundle):
        return self._is_authorized_detail(object_list, bundle)

    def delete_list(self, object_list, bundle):
        return self._is_authorized_list(object_list, bundle)

    def delete_detail(self, object_list, bundle):
        return self._is_authorized_detail(object_list, bundle)
