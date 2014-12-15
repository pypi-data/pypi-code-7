'''
InheritanceQuerySet and InheritanceManager taken from django-model-utils:
https://bitbucket.org/carljm/django-model-utils/src/3b66a0a41a61/model_utils/managers.py
'''
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.fields.related import OneToOneField
from django.db.models.query import QuerySet


class InheritanceQuerySet(QuerySet):
    def select_subclasses(self, *subclasses):
        if not subclasses:
            subclasses = [rel.var_name for rel in self.model._meta.get_all_related_objects()
                          if isinstance(rel.field, OneToOneField)
                          and issubclass(rel.field.model, self.model)]
        new_qs = self.select_related(*subclasses)
        new_qs.subclasses = subclasses
        return new_qs

    def _clone(self, klass=None, setup=False, **kwargs):
        for name in ['subclasses', '_annotated']:
            if hasattr(self, name):
                kwargs[name] = getattr(self, name)
        return super(InheritanceQuerySet, self)._clone(klass, setup, **kwargs)

    def annotate(self, *args, **kwargs):
        qset = super(InheritanceQuerySet, self).annotate(*args, **kwargs)
        qset._annotated = [a.default_alias for a in args] + kwargs.keys()
        return qset

    def iterator(self):
        iter = super(InheritanceQuerySet, self).iterator()
        if getattr(self, 'subclasses', False):
            for obj in iter:
                sub_obj = []
                for s in self.subclasses:
                    try:
                        sub_obj.append(getattr(obj, s))
                    except ObjectDoesNotExist:
                        pass
                if not sub_obj:
                    sub_obj = [obj]
                sub_obj = sub_obj[0]
                if getattr(self, '_annotated', False):
                    for k in self._annotated:
                        setattr(sub_obj, k, getattr(obj, k))

                yield sub_obj
        else:
            for obj in iter:
                yield obj


class InheritanceManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return InheritanceQuerySet(self.model)

    def select_subclasses(self, *subclasses):
        return self.get_queryset().select_subclasses(*subclasses)

    def get_subclass(self, *args, **kwargs):
        return self.get_queryset().select_subclasses().get(*args, **kwargs)
