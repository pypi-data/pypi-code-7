from django.db import models
from django.conf import settings
from django.utils import translation
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist

import reversion
from polymorphic import PolymorphicModel
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager


class TranslatedModel(models.Model):
    class Meta:
        abstract = True

    @property
    def translation(self):
        language_code = translation.get_language()
        try:
            return self.translations.get(language=language_code)
        except ObjectDoesNotExist:
            return self.translations.get(language=settings.LANGUAGE_CODE)


class AbstractTranslation(models.Model):
    # https://code.djangoproject.com/ticket/16732
    class Meta:
        abstract = True
        #unique_together = (('master', 'language'),)

    @property
    def master(self):
        raise ImproperlyConfigured

    language = models.CharField(max_length=7, choices=settings.LANGUAGES)


class Category(TranslatedModel, MPTTModel):
    slug = models.SlugField(max_length=255)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    def __str__(self):
        return self.translation.name


class CategoryTranslation(AbstractTranslation):
    class Meta:
        unique_together = (('master', 'language'),)
    master = models.ForeignKey('Category', related_name='translations')

    name = models.CharField(max_length=255)
    descrition = models.TextField(blank=True)


class Content(TranslatedModel, PolymorphicModel):
    slug = models.SlugField(max_length=255)
    published = models.BooleanField(default=True)

    def __str__(self):
        return self.translation.title
        

class ContentTranslation(AbstractTranslation):
    class Meta:
        unique_together = (('master', 'language'),)

    master = models.ForeignKey('Content', related_name='translations')

    title = models.CharField(max_length=255)
    

class BaseArticle(Content):
    publication_time = models.DateTimeField()
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name="authors")
    categories = models.ManyToManyField(Category)
    tags = TaggableManager(blank=True)


class BaseArticleTranslation(ContentTranslation):
    body = models.TextField()


class Article(BaseArticle):
    image = models.ForeignKey('MediaItem')


class Page(Content):
    pass


class PageTranslation(ContentTranslation):
    class Meta:
        abstract = True
    body = models.TextField()
    

class MediaItem(Content):
    file = models.FileField()
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.file.url


class MediaCollection(Content):
    items = models.ManyToManyField(MediaItem)


reversion.register(Category, follow=('translations', ))
reversion.register(CategoryTranslation)
reversion.register(Content, follow=('translations', ))
reversion.register(ContentTranslation)
reversion.register(BaseArticle, follow=('categories', 'authors', ))
reversion.register(BaseArticleTranslation)