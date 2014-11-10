# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User, Group
from geoprisma.models import Resource, Session


#Dummy decorator if schema is not supported
def schematize(original_class):
        return original_class

#Import model that support PGSQL schema if difined
if hasattr(settings,'SCHEMATIZED_MODELS'):
        try:
                models = __import__(settings.SCHEMATIZED_MODELS, fromlist=['*'])
                schematize = models.schematize
        except ImportError:
                from django.db import models
else:
        from django.db import models

@schematize
class Action(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)
        verbose_name = "Action"
        verbose_name_plural = "Actions"

    def __unicode__(self):
        return self.name

@schematize
class Right(models.Model):
        id_group = models.ForeignKey(Group)
        id_resource = models.ForeignKey(Resource)
        actions = models.ManyToManyField(Action)

        class Meta:
                ordering = ('id_group', 'id_resource',)
                unique_together = ('id_group', 'id_resource',)
                verbose_name = "Right"
                verbose_name_plural = "Rights"

        def __unicode__(self):
                return "%s - %s" % (self.id_group, self.id_resource,)
