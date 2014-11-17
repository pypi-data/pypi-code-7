import datetime

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models

class SiteNewsCategory(models.Model):
    site = models.ForeignKey(Site)
    code = models.CharField(max_length=255, unique=True)
    url = models.SlugField(max_length=255, unique=True)
    label = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'site news categories'
    
    def __unicode__(self):
        return u'%s' % self.label


class SiteNewsArticle(models.Model):
    sitenewscategory = models.ForeignKey(SiteNewsCategory)
    author = models.ForeignKey(User)
    url = models.SlugField(max_length=255)
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    create_date = models.DateTimeField(default=datetime.datetime.now)
    modify_date = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(blank=True, null=True)
    published = models.BooleanField(default=False)


    class Meta:
        unique_together = ('sitenewscategory', 'url')
        ordering = ('-publish_date',)

    def __unicode__(self):
        return u'%s' % self.title

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            kwargs['initial'] = request.user.id
        return super(MyModelAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def get_absolute_url(self):
        return reverse('news-detail', args=[self.sitenewscategory.url, self.url])
