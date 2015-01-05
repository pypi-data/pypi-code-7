from rest_framework import permissions, status

from uuidfield.fields import StringUUID

from mobile_framework import get_device_model, get_app_user_model

AppUser = get_app_user_model()
Device = get_device_model()


class IsSameDeviceOrReadOnly(permissions.BasePermission):
    """
    Allows access if the request is coming from the same device that the current
    logged in user is currently logged in at.
    """
    def has_permission(self, request, view):
        device_uuid = request.META.get('HTTP_X_DEVICE', None)

        return (
            (request.user.is_authenticated() and (request.user.is_staff or
            request.user.app_user.device.uuid == StringUUID(device_uuid))) or
            request.method in permissions.SAFE_METHODS
        )


class IsSameUserOrReadOnly(permissions.BasePermission):
    """
    Allows access if the currently logged in user is the same user that is to be
    updated.
    """
    def has_permission(self, request, view):
        """
        Checks if the user is the same user being edited or deleted.
        """
        kwargs = getattr(view, 'kwargs', None)
        user_id = kwargs.get('pk', None)
        user = request.user

        try:
            pk = str(user.app_user.pk)
        except (AttributeError, AppUser.DoesNotExist):
            pk = str(user.pk)

        return (
            (request.user.is_authenticated() and (user_id == pk or 
            user.is_staff)) or request.method in permissions.SAFE_METHODS
        )