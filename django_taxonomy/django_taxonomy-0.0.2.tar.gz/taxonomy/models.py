from django.db import models

from mptt.models import MPTTModel, TreeForeignKey


class TaxonomyModel(MPTTModel):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    weight = models.DecimalField(db_index=True, default=0, max_digits=5, decimal_places=2)
    published = models.BooleanField(db_index=True, default=True)

    class Meta:
        abstract = True

    class MPTTMeta:
        order_insertion_by = ['weight']

    def published_children(self):
        return self.children.filter(published=True)

    def __init__(self, *args, **kwargs):
        super(TaxonomyModel, self).__init__(*args, **kwargs)
        self._starting_weight = self.weight

    def save(self, *args, **kwargs):
        super(TaxonomyModel, self).save(*args, **kwargs)
        if self._starting_weight != self.weight:
            self.__class__.objects.rebuild()
