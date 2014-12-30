from django.contrib.contenttypes.models import ContentType


class Base(object):
    """
        A singletonish (based on id) type with additional
        equality functionality
    """
    _registry = None  ## should be overridden, don't share through base

    def __init__(self, id, name="", description=""):
        self.id = id
        self.name = name or id
        self.description = description

    def __eq__(self, other):
        return other and self.__class__ is other.__class__ and \
               self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def create(cls, id, name="", description=""):
        p = cls._registry.get(id)
        if not p:
            p = cls(id, name, description)
            cls._registry[id] = p
        return p

    @classmethod
    def all(cls):
        return cls._registry.values()

class Permission(Base):
    _registry = {}

    def __unicode__(self):
        return u"<Permission {0} ({1})>".format(self.id, self.name)

    __repr__ = __unicode__

class Role(Base):
    _registry = {}

    def has_access(self, obj, permission):
        from .models import RolePermission
        model_ct = ContentType.objects.get_for_model(obj)
        return RolePermission.objects.filter(content_type=model_ct,
                                             object_id=obj.id,
                                             role=self,
                                             permission=permission).exists()

    def __unicode__(self):
        return u"<Role {0} ({1})>".format(self.id, self.name)

    __repr__ = __unicode__
