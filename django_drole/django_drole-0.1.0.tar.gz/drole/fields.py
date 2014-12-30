from django.db import models
from .types import Role, Permission

class RoleField(models.CharField):

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value is None:
            return None

        if isinstance(value, (str, unicode)):
            return Role(value)

        return value

    def get_prep_value(self, value):
        if isinstance(value, Role):
            return value.id
        return value


class PermissionField(models.CharField):

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value is None:
            return None

        if isinstance(value, (str, unicode)):
            return Permission(value)

        return value

    def get_prep_value(self, value):
        if isinstance(value, Permission):
            return value.id
        return value

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^drole\.fields\.RoleField"])
add_introspection_rules([], ["^drole\.fields\.PermissionField"])
