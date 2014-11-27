from django.db import models
from django import forms
from django.utils.text import slugify
from os import path
try:
    from conf.settings import DJBIBLIO_MAX_SIZE
except ImportError:
    DJBIBLIO_MAX_SIZE = (33554432 , '32MB')

class Project(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']
#    def get_absolute_url(self):
#        return '/biblio/project/%d/' % self.id

class WorkFileField(models.FileField):
    def __init__(self, *args, **kwargs):
        self.max_size = kwargs.pop('max_size', 0)
        self.max_help = kwargs.pop('max_help', 'unlimited')
        super(WorkFileField, self).__init__(*args, **kwargs)
    def clean(self, *args, **kwargs):
        data = super(WorkFileField, self).clean(*args, **kwargs)
        if self.max_size and self.max_size < data.size:
            ftb = 'Sorry, file must be smaller than %s' % self.max_help
            raise forms.ValidationError(ftb, code='filetoobig')
        return data

def upload_work(slug, file):
    fname, ext = path.splitext(file)
    return 'work/' + slug + '/' + slugify(fname) + ext
def upload_work_inst(inst, file):
    return upload_work(inst.slug, file)

class Work(models.Model):
    mnemonic = models.CharField(max_length=120)
    slug     = models.SlugField(unique=True)
    abstract = models.TextField(max_length=2000, blank=True)
    workurl  = models.URLField(verbose_name="Work's URL")
    upload   = WorkFileField( upload_to=upload_work_inst
                            , blank=True
                            , max_size=DJBIBLIO_MAX_SIZE[0]
                            , max_help=DJBIBLIO_MAX_SIZE[1] )
    projects = models.ManyToManyField(Project, related_name='works')
    def __unicode__(self):
        return self.mnemonic
#    def get_absolute_url(self):
#        return '/biblio/work/%d/' % self.id
    class Meta:
        ordering = ['mnemonic']

class Bibtag(models.Model):
    tag   = models.CharField(verbose_name='Field Name', max_length=20)
    value = models.TextField(max_length=1000)
    work  = models.ForeignKey(Work, related_name='bibtags')
    def __unicode__(self):
        return '%s : %s' % ( self.tag , self.value[0:60] )
    class Meta:
        unique_together = ['tag', 'work']
        ordering        = ['tag']
#    def get_absolute_url(self):
#        return '/biblio/bibtag/%d/' % self.id

# Author is *not* meant as a substitute for the author bibtex tag, neither will
# it be updated if the tag is updated.  It is only meant as and extra index
# that is generated when the input bibtex is parsed for the first time.
class Author(models.Model):
    name  = models.CharField(max_length=255, unique=True)
    works = models.ManyToManyField(Work, related_name='authors')
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']
#    def get_absolute_url(self):
#        return '/biblio/author/%d/' % self.id

