from django.contrib.contenttypes.models import ContentType
from django.db import models


class PolyMorph(models.Model):

    class Meta(object):
        app_label = "simple_polymorph"
        abstract = True

    real_type = models.ForeignKey(ContentType, null=True, blank=True, editable=False)

    def save(self, **kwargs):
        if not self.real_type:
            self.real_type = ContentType.objects.get_for_model(self)
        super(PolyMorph, self).save(**kwargs)

    def polymorph(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)
