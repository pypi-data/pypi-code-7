from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from .fields import RoleField, PermissionField

class RolePermission(models.Model):
    permission = PermissionField(max_length=255, blank=False, db_index=True)
    role = RoleField(max_length=255, blank=False, db_index=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    @classmethod
    def clear(cls, obj, permission):
        """ clear all role assignments for permission on instance """
        model_ct = ContentType.objects.get_for_model(obj)
        cls.objects.filter(content_type=model_ct, object_id=obj.id,
                           permission=permission).delete()

    @classmethod
    def assign(cls, obj, role, permission):
        model_ct = ContentType.objects.get_for_model(obj)
        r, _ = cls.objects.get_or_create(content_type=model_ct,
                                         object_id=obj.id,
                                         permission=permission,
                                         role=role)
        return r

    @classmethod
    def assignments(cls, obj):  # XXX make this a manager?
        """ return all assignments for a specific object """
        model_ct = ContentType.objects.get_for_model(obj)
        return cls.objects.filter(content_type=model_ct, object_id=obj.id).all()


    def __unicode__(self):
        return u"<Permission {0} for role {1}>".format(self.permission,
                                                      self.role)
